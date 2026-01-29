# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class DashboardTaiSan(models.TransientModel):
    _name = 'dashboard.tai_san'
    _description = 'Dashboard Quản lý Tài sản'
    
    @api.model
    def get_dashboard_data(self):
        """Lấy dữ liệu tổng quan cho dashboard"""
        TaiSan = self.env['tai_san']
        BaoTri = self.env['bao_tri_tai_san']
        
        # Thống kê tổng quan
        tong_tai_san = TaiSan.search_count([])
        all_assets = TaiSan.search([])
        
        tong_gia_tri = sum(all_assets.mapped('gia_tri'))
        tong_gia_tri_con_lai = sum(all_assets.mapped('gia_tri_con_lai'))
        tong_da_khau_hao = sum(all_assets.mapped('tong_gia_tri_da_khau_hao'))
        
        # Thống kê theo trạng thái
        dang_su_dung = TaiSan.search_count([('vi_tri', '=', 'dang_su_dung')])
        trong_kho = TaiSan.search_count([('vi_tri', '=', 'kho')])
        dang_bao_tri = TaiSan.search_count([('vi_tri', '=', 'bao_tri')])
        da_thanh_ly = TaiSan.search_count([('tinh_trang', '=', 'da_thanh_ly')])
        
        # Tài sản cần bảo trì
        can_bao_tri = TaiSan.search_count([('tinh_trang', '=', 'can_bao_tri')])
        tai_san_hong = TaiSan.search_count([('tinh_trang', '=', 'hong')])
        
        # Thống kê theo loại
        theo_loai = []
        loai_tai_san_list = dict(TaiSan._fields['loai_tai_san'].selection)
        for key, label in loai_tai_san_list.items():
            tai_san_theo_loai = TaiSan.search([('loai_tai_san', '=', key)])
            if tai_san_theo_loai:
                theo_loai.append({
                    'loai': label,
                    'so_luong': len(tai_san_theo_loai),
                    'gia_tri': sum(tai_san_theo_loai.mapped('gia_tri')),
                    'gia_tri_con_lai': sum(tai_san_theo_loai.mapped('gia_tri_con_lai')),
                })
        
        # Cảnh báo bảo trì sắp tới (30 ngày)
        today = fields.Date.today()
        next_month = today + timedelta(days=30)
        
        bao_tri_sap_toi = BaoTri.search([
            ('ngay_bao_tri_tiep_theo', '>=', today),
            ('ngay_bao_tri_tiep_theo', '<=', next_month),
            ('trang_thai', '=', 'hoan_thanh')
        ])
        
        canh_bao_bao_tri = []
        for bao_tri in bao_tri_sap_toi:
            ngay_con_lai = (bao_tri.ngay_bao_tri_tiep_theo - today).days
            canh_bao_bao_tri.append({
                'tai_san': bao_tri.tai_san_id.name,
                'ma_tai_san': bao_tri.tai_san_id.ma_tai_san,
                'ngay_bao_tri': bao_tri.ngay_bao_tri_tiep_theo.strftime('%d/%m/%Y'),
                'ngay_con_lai': ngay_con_lai,
                'muc_do': 'cao' if ngay_con_lai <= 7 else 'trung_binh',
            })
        
        # Top 10 tài sản giá trị cao nhất
        top_tai_san = TaiSan.search([], order='gia_tri desc', limit=10)
        top_list = []
        for ts in top_tai_san:
            top_list.append({
                'name': ts.name,
                'ma_tai_san': ts.ma_tai_san,
                'gia_tri': ts.gia_tri,
                'gia_tri_con_lai': ts.gia_tri_con_lai,
                'ty_le_khau_hao': ts.ty_le_khau_hao_hoan_thanh,
            })
        
        # Tài sản đã khấu hao gần hết (>90%)
        sap_het_khau_hao = TaiSan.search([
            ('ty_le_khau_hao_hoan_thanh', '>=', 90),
            ('tinh_trang', '!=', 'da_thanh_ly')
        ])
        
        # Thống kê chi phí bảo trì
        tong_chi_phi_bao_tri = sum(BaoTri.search([('trang_thai', '=', 'hoan_thanh')]).mapped('chi_phi'))
        
        # Biểu đồ khấu hao theo tháng (12 tháng gần nhất)
        bieu_do_khau_hao = self._get_bieu_do_khau_hao()
        
        return {
            # Tổng quan
            'tong_tai_san': tong_tai_san,
            'tong_gia_tri': tong_gia_tri,
            'tong_gia_tri_con_lai': tong_gia_tri_con_lai,
            'tong_da_khau_hao': tong_da_khau_hao,
            'ty_le_khau_hao_trung_binh': (tong_da_khau_hao / tong_gia_tri * 100) if tong_gia_tri > 0 else 0,
            
            # Theo trạng thái
            'dang_su_dung': dang_su_dung,
            'trong_kho': trong_kho,
            'dang_bao_tri': dang_bao_tri,
            'da_thanh_ly': da_thanh_ly,
            
            # Cảnh báo
            'can_bao_tri': can_bao_tri,
            'tai_san_hong': tai_san_hong,
            'canh_bao_bao_tri': canh_bao_bao_tri,
            'canh_bao_bao_tri_count': len(canh_bao_bao_tri),
            'sap_het_khau_hao': len(sap_het_khau_hao),
            
            # Phân tích
            'theo_loai': theo_loai,
            'top_tai_san': top_list,
            'tong_chi_phi_bao_tri': tong_chi_phi_bao_tri,
            'bieu_do_khau_hao': bieu_do_khau_hao,
        }
    
    def _get_bieu_do_khau_hao(self):
        """Tạo dữ liệu biểu đồ khấu hao 12 tháng gần nhất"""
        TaiSan = self.env['tai_san']
        today = datetime.today()
        
        labels = []
        khau_hao_data = []
        
        for i in range(11, -1, -1):
            month_date = today - timedelta(days=30*i)
            labels.append(month_date.strftime('%m/%Y'))
            
            # Tính tổng khấu hao trong tháng
            # (Simplified - trong thực tế cần tính chính xác hơn)
            total_monthly = sum(TaiSan.search([]).mapped('gia_tri_khau_hao_hang_thang'))
            khau_hao_data.append(total_monthly)
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Khấu hao hàng tháng (VNĐ)',
                'data': khau_hao_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2,
            }]
        }
    
    @api.model
    def get_tai_san_theo_phong_ban(self):
        """Thống kê tài sản theo phòng ban"""
        TaiSan = self.env['tai_san']
        PhongBan = self.env['phong_ban']
        
        result = []
        for phong_ban in PhongBan.search([]):
            tai_san_ids = TaiSan.search([('phong_ban_id', '=', phong_ban.id)])
            if tai_san_ids:
                result.append({
                    'phong_ban': phong_ban.name,
                    'so_luong': len(tai_san_ids),
                    'tong_gia_tri': sum(tai_san_ids.mapped('gia_tri')),
                    'gia_tri_con_lai': sum(tai_san_ids.mapped('gia_tri_con_lai')),
                })
        
        return result
    
    @api.model
    def export_bao_cao_khau_hao(self, year=None):
        """Xuất báo cáo khấu hao theo năm"""
        if not year:
            year = datetime.today().year
        
        TaiSan = self.env['tai_san']
        tai_san_ids = TaiSan.search([
            ('ngay_mua', '>=', f'{year}-01-01'),
            ('ngay_mua', '<=', f'{year}-12-31'),
        ])
        
        bao_cao = []
        for ts in tai_san_ids:
            bao_cao.append({
                'ma_tai_san': ts.ma_tai_san,
                'ten_tai_san': ts.name,
                'ngay_mua': ts.ngay_mua.strftime('%d/%m/%Y') if ts.ngay_mua else '',
                'gia_tri_mua': ts.gia_tri,
                'phuong_phap_khau_hao': dict(ts._fields['phuong_phap_khau_hao'].selection).get(ts.phuong_phap_khau_hao),
                'thoi_gian_khau_hao': f"{ts.thoi_gian_khau_hao} năm",
                'khau_hao_hang_nam': ts.gia_tri_khau_hao_hang_nam,
                'khau_hao_hang_thang': ts.gia_tri_khau_hao_hang_thang,
                'tong_da_khau_hao': ts.tong_gia_tri_da_khau_hao,
                'gia_tri_con_lai': ts.gia_tri_con_lai,
                'ty_le_hoan_thanh': f"{ts.ty_le_khau_hao_hoan_thanh:.2f}%",
            })
        
        return bao_cao
