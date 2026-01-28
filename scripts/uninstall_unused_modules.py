#!/usr/bin/env python3
"""
Script tự động gỡ cài đặt các module Odoo không cần thiết
Chỉ giữ lại 3 module chính: Nhân Sự, Quản Lý Phòng Họp, Quản Lý Tài Sản
"""

import psycopg2
import sys

# Cấu hình database
DB_NAME = "quan_ly_tai_san_va_phong_hop"
DB_USER = "odoo"
DB_PASSWORD = "odoo"
DB_HOST = "localhost"
DB_PORT = "5435"

# Danh sách module CẦN GIỮ LẠI
KEEP_MODULES = [
    'base',
    'web',
    'mail',
    'bus',
    'web_tour',
    'base_setup',
    'web_editor',
    'web_kanban_gauge',
    'web_unsplash',
    'iap',
    'iap_mail',
    'partner_autocomplete',
    'phone_validation',
    'sms',
    'snailmail',
    'auth_signup',
    'auth_totp',
    'auth_totp_mail',
    'base_import',
    'fetchmail',
    'mail_bot',
    # Module tự phát triển
    'nhan_su',
    'quan_li_phong_hop_hoi_truong',
    'quan_ly_tai_san',
]

def connect_db():
    """Kết nối đến database PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Lỗi kết nối database: {e}")
        sys.exit(1)

def get_installed_modules(conn):
    """Lấy danh sách tất cả module đã cài đặt"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, display_name, state 
        FROM ir_module_module 
        WHERE state IN ('installed', 'to upgrade', 'to install')
        ORDER BY name;
    """)
    modules = cursor.fetchall()
    cursor.close()
    return modules

def uninstall_module(conn, module_name):
    """Gỡ cài đặt một module"""
    cursor = conn.cursor()
    try:
        # Đánh dấu module để gỡ cài đặt
        cursor.execute("""
            UPDATE ir_module_module 
            SET state = 'to remove' 
            WHERE name = %s AND state = 'installed';
        """, (module_name,))
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"  ⚠️  Lỗi khi gỡ {module_name}: {e}")
        conn.rollback()
        cursor.close()
        return False

def main():
    print("=" * 70)
    print("🔧 SCRIPT TỰ ĐỘNG GỠ MODULE ODOO KHÔNG CẦN THIẾT")
    print("=" * 70)
    print()
    
    # Kết nối database
    print("📡 Đang kết nối database...")
    conn = connect_db()
    print("✅ Kết nối thành công!\n")
    
    # Lấy danh sách module đã cài
    print("📋 Đang lấy danh sách module đã cài đặt...")
    installed_modules = get_installed_modules(conn)
    print(f"✅ Tìm thấy {len(installed_modules)} module đã cài đặt\n")
    
    # Lọc module cần gỡ
    modules_to_remove = []
    for name, display_name, state in installed_modules:
        if name not in KEEP_MODULES:
            modules_to_remove.append((name, display_name))
    
    if not modules_to_remove:
        print("✅ Không có module nào cần gỡ!")
        conn.close()
        return
    
    # Hiển thị danh sách module sẽ gỡ
    print(f"📦 Danh sách {len(modules_to_remove)} module SẼ GỠ:")
    print("-" * 70)
    for idx, (name, display_name) in enumerate(modules_to_remove, 1):
        print(f"{idx:3}. {display_name} ({name})")
    print("-" * 70)
    print()
    
    # Hiển thị module sẽ giữ lại
    print(f"✅ Danh sách {len(KEEP_MODULES)} module SẼ GIỮ LẠI:")
    print("-" * 70)
    kept_modules = [(name, display_name) for name, display_name, state in installed_modules if name in KEEP_MODULES]
    for idx, (name, display_name) in enumerate(kept_modules, 1):
        print(f"{idx:3}. {display_name} ({name})")
    print("-" * 70)
    print()
    
    # Xác nhận
    response = input("❓ Bạn có chắc chắn muốn gỡ các module trên? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Hủy bỏ thao tác!")
        conn.close()
        return
    
    print()
    print("🚀 Bắt đầu gỡ cài đặt...")
    print("-" * 70)
    
    # Gỡ từng module
    success_count = 0
    failed_count = 0
    
    for name, display_name in modules_to_remove:
        print(f"🗑️  Đang gỡ: {display_name} ({name})...", end=" ")
        if uninstall_module(conn, name):
            print("✅")
            success_count += 1
        else:
            print("❌")
            failed_count += 1
    
    print("-" * 70)
    print()
    print("📊 KẾT QUẢ:")
    print(f"  ✅ Gỡ thành công: {success_count} module")
    if failed_count > 0:
        print(f"  ❌ Gỡ thất bại: {failed_count} module")
    print()
    
    # Đóng kết nối
    conn.close()
    
    print("=" * 70)
    print("✅ HOÀN THÀNH!")
    print("=" * 70)
    print()
    print("📝 BƯỚC TIẾP THEO:")
    print("  1. Restart Odoo server")
    print("  2. Chạy lệnh: python3 odoo-bin -c odoo.conf -u base -d quan_ly_tai_san_va_phong_hop")
    print("  3. Truy cập: http://localhost:8069")
    print()
    print("⚠️  LƯU Ý: Sau khi restart, Odoo sẽ thực hiện gỡ cài đặt các module!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bỏ!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        sys.exit(1)
