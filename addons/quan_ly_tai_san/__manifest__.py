# -*- coding: utf-8 -*-
{
    'name': "Quản lý Tài sản",

    'summary': """
        Quản lý tài sản, thiết bị của trường - Liên kết với Nhân sự và Phòng họp""",

    'description': """
        Module quản lý tài sản bao gồm:
        - Quản lý thông tin tài sản (máy tính, thiết bị, bàn ghế...)
        - Theo dõi lịch sử sử dụng tài sản
        - Quản lý bảo trì, sửa chữa
        - Chuyển giao tài sản giữa phòng ban/nhân viên
        - Kiểm kê tài sản định kỳ
        - Tính toán khấu hao tự động (3 phương pháp)
        - Dashboard tổng quan và phân tích
        - Mã QR code cho tài sản
        - Liên kết với module Nhân sự và Phòng họp
    """,

    'author': "TTDN-16-05-N4",
    'website': "https://github.com/Nemmer772004/TTDN-16-05-N4",

    'category': 'Operations',
    'version': '2.0',
    'license': 'LGPL-3',

    # Module phụ thuộc
    'depends': ['base', 'mail', 'quan_ly_nhan_su', 'web'],

    # Dữ liệu luôn load
    'data': [
        'security/ir.model.access.csv',
        'data/tai_san_sequence.xml',
        'views/tai_san_views.xml',
        'views/lich_su_su_dung_views.xml',
        'views/bao_tri_views.xml',
        'views/chuyen_giao_views.xml',
        'views/kiem_ke_views.xml',
        'views/dashboard_views.xml',
        'views/report_templates.xml',
        'views/menu.xml',
    ],

    # Assets (JS, CSS, XML templates)
    'assets': {
        'web.assets_backend': [
            'quan_ly_tai_san/static/src/css/dashboard.css',
            'quan_ly_tai_san/static/src/js/dashboard.js',
        ],
        'web.assets_qweb': [
            'quan_ly_tai_san/static/src/xml/dashboard_templates.xml',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
