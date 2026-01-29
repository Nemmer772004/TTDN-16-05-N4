# -*- coding: utf-8 -*-
from odoo import models, fields, api


class KhauHaoTaiSan(models.Model):
    _name = 'khau_hao.tai_san'
    _description = 'Lịch sử Khấu hao Tài sản'
    _order = 'thang_nam desc'
    
    tai_san_id = fields.Many2one(
        'tai_san',
        string='Tài sản',
        required=True,
        ondelete='cascade',
        index=True
    )
    ma_tai_san = fields.Char(
        related='tai_san_id.ma_tai_san',
        string='Mã tài sản',
        store=True,
        readonly=True
    )
    thang_nam = fields.Date(
        string='Tháng/Năm',
        required=True,
        index=True
    )
    nam_thu = fields.Integer(
        string='Năm thứ',
        help='Năm thứ mấy trong thời gian khấu hao'
    )
    gia_tri_khau_hao = fields.Float(
        string='Giá trị Khấu hao',
        digits=(16, 2),
        help='Giá trị khấu hao trong tháng/kỳ này'
    )
    gia_tri_luy_ke = fields.Float(
        string='Giá trị Lũy kế',
        digits=(16, 2),
        help='Tổng giá trị đã khấu hao đến thời điểm này'
    )
    gia_tri_con_lai = fields.Float(
        string='Giá trị còn lại',
        digits=(16, 2),
        help='Giá trị còn lại sau khấu hao'
    )
    phuong_phap = fields.Selection([
        ('duong_thang', 'Đường thẳng'),
        ('so_du_giam_dan', 'Số dư giảm dần'),
        ('tong_so_nam', 'Tổng số năm'),
    ], string='Phương pháp', readonly=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    
    _sql_constraints = [
        ('unique_tai_san_thang_nam', 'unique(tai_san_id, thang_nam)',
         'Đã có bản ghi khấu hao cho tài sản này trong tháng này!'),
    ]
    
    @api.model
    def create_khau_hao_record(self, tai_san, thang_nam, nam_thu, gia_tri_khau_hao, 
                               gia_tri_luy_ke, gia_tri_con_lai):
        """
        Tạo bản ghi khấu hao cho tài sản
        
        Args:
            tai_san: recordset tai_san
            thang_nam: date - tháng năm khấu hao
            nam_thu: int - năm thứ mấy
            gia_tri_khau_hao: float - giá trị khấu hao kỳ này
            gia_tri_luy_ke: float - tổng lũy kế
            gia_tri_con_lai: float - giá trị còn lại
        """
        return self.create({
            'tai_san_id': tai_san.id,
            'thang_nam': thang_nam,
            'nam_thu': nam_thu,
            'gia_tri_khau_hao': gia_tri_khau_hao,
            'gia_tri_luy_ke': gia_tri_luy_ke,
            'gia_tri_con_lai': gia_tri_con_lai,
            'phuong_phap': tai_san.phuong_phap_khau_hao,
        })
    
    @api.model
    def generate_khau_hao_schedule(self, tai_san):
        """
        Tạo lịch khấu hao cho toàn bộ thời gian sử dụng tài sản
        
        Gọi function này để tạo đầy đủ các bản ghi khấu hao
        cho tài sản theo phương pháp đã chọn
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        if not tai_san.ngay_bat_dau_su_dung or tai_san.thoi_gian_khau_hao <= 0:
            return
        
        # Xóa các bản ghi cũ (nếu có)
        self.search([('tai_san_id', '=', tai_san.id)]).unlink()
        
        ngay_bat_dau = tai_san.ngay_bat_dau_su_dung
        so_thang = tai_san.thoi_gian_khau_hao * 12
        gia_tri_khau_hao_thang = tai_san.gia_tri_khau_hao_hang_thang
        tong_luy_ke = 0.0
        gia_tri_ban_dau = tai_san.gia_tri
        gia_tri_thanh_ly = tai_san.gia_tri_thanh_ly
        gia_tri_khau_hao_toi_da = gia_tri_ban_dau - gia_tri_thanh_ly
        
        # Xử lý theo phương pháp khấu hao
        if tai_san.phuong_phap_khau_hao == 'duong_thang':
            # Đường thẳng: Khấu hao đều mỗi tháng
            for thang in range(int(so_thang)):
                ngay_khau_hao = ngay_bat_dau + relativedelta(months=thang)
                nam_thu = (thang // 12) + 1
                
                # Khấu hao tháng này
                khau_hao_thang = gia_tri_khau_hao_thang
                
                # Kiểm tra không vượt quá giá trị thanh lý
                if tong_luy_ke + khau_hao_thang > gia_tri_khau_hao_toi_da:
                    khau_hao_thang = gia_tri_khau_hao_toi_da - tong_luy_ke
                
                tong_luy_ke += khau_hao_thang
                gia_tri_con_lai = gia_tri_ban_dau - tong_luy_ke
                
                self.create_khau_hao_record(
                    tai_san, ngay_khau_hao, nam_thu,
                    khau_hao_thang, tong_luy_ke, gia_tri_con_lai
                )
                
                if tong_luy_ke >= gia_tri_khau_hao_toi_da:
                    break
        
        elif tai_san.phuong_phap_khau_hao == 'so_du_giam_dan':
            # Số dư giảm dần: Khấu hao nhiều ở đầu
            ty_le_nam = 2.0 / tai_san.thoi_gian_khau_hao
            gia_tri_hien_tai = gia_tri_ban_dau
            
            for nam in range(tai_san.thoi_gian_khau_hao):
                # Khấu hao năm này
                khau_hao_nam = gia_tri_hien_tai * ty_le_nam
                
                # Kiểm tra không vượt quá
                if tong_luy_ke + khau_hao_nam > gia_tri_khau_hao_toi_da:
                    khau_hao_nam = gia_tri_khau_hao_toi_da - tong_luy_ke
                
                # Chia đều cho 12 tháng trong năm
                khau_hao_thang = khau_hao_nam / 12.0
                
                for thang in range(12):
                    ngay_khau_hao = ngay_bat_dau + relativedelta(months=nam*12 + thang)
                    
                    if tong_luy_ke + khau_hao_thang > gia_tri_khau_hao_toi_da:
                        khau_hao_thang = gia_tri_khau_hao_toi_da - tong_luy_ke
                    
                    tong_luy_ke += khau_hao_thang
                    gia_tri_con_lai = gia_tri_ban_dau - tong_luy_ke
                    
                    self.create_khau_hao_record(
                        tai_san, ngay_khau_hao, nam + 1,
                        khau_hao_thang, tong_luy_ke, gia_tri_con_lai
                    )
                    
                    if tong_luy_ke >= gia_tri_khau_hao_toi_da:
                        break
                
                if tong_luy_ke >= gia_tri_khau_hao_toi_da:
                    break
                
                gia_tri_hien_tai -= khau_hao_nam
        
        elif tai_san.phuong_phap_khau_hao == 'tong_so_nam':
            # Tổng số năm
            tong_nam = tai_san.thoi_gian_khau_hao
            tong_so = (tong_nam * (tong_nam + 1)) / 2
            
            for nam in range(tong_nam):
                nam_con_lai = tong_nam - nam
                ty_le_nam = nam_con_lai / tong_so
                khau_hao_nam = gia_tri_khau_hao_toi_da * ty_le_nam
                khau_hao_thang = khau_hao_nam / 12.0
                
                for thang in range(12):
                    ngay_khau_hao = ngay_bat_dau + relativedelta(months=nam*12 + thang)
                    
                    if tong_luy_ke + khau_hao_thang > gia_tri_khau_hao_toi_da:
                        khau_hao_thang = gia_tri_khau_hao_toi_da - tong_luy_ke
                    
                    tong_luy_ke += khau_hao_thang
                    gia_tri_con_lai = gia_tri_ban_dau - tong_luy_ke
                    
                    self.create_khau_hao_record(
                        tai_san, ngay_khau_hao, nam + 1,
                        khau_hao_thang, tong_luy_ke, gia_tri_con_lai
                    )
                    
                    if tong_luy_ke >= gia_tri_khau_hao_toi_da:
                        break
                
                if tong_luy_ke >= gia_tri_khau_hao_toi_da:
                    break
