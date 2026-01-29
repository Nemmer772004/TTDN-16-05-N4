# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ChiTietKiemKe(models.Model):
    _name = 'chi_tiet_kiem_ke'
    _description = 'Chi tiết kiểm kê tài sản'
    _order = 'kiem_ke_id, tai_san_id'

    kiem_ke_id = fields.Many2one('kiem_ke_tai_san', string='Phiếu kiểm kê', required=True, ondelete='cascade')
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', required=True)
    ma_tai_san = fields.Char(related='tai_san_id.ma_tai_san', string='Mã tài sản', readonly=True)
    ten_tai_san = fields.Char(related='tai_san_id.name', string='Tên tài sản', readonly=True)
    
    # Thông tin sổ sách
    gia_tri_so_sach = fields.Float(string='Giá trị sổ sách', readonly=True)
    tinh_trang_so_sach = fields.Selection([
        ('moi', 'Mới'),
        ('tot', 'Tốt'),
        ('binh_thuong', 'Bình thường'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hu_hong', 'Hư hỏng'),
        ('mat', 'Mất'),
        ('da_thanh_ly', 'Đã thanh lý'),
    ], string='Tình trạng sổ sách', readonly=True)
    vi_tri_so_sach = fields.Selection([
        ('kho', 'Kho'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Bảo trì'),
        ('dang_chuyen_giao', 'Đang chuyển giao'),
    ], string='Vị trí sổ sách', readonly=True)
    
    # Thông tin thực tế
    co_thuc_te = fields.Boolean(string='Có thực tế', default=True)
    gia_tri_thuc_te = fields.Float(string='Giá trị thực tế')
    tinh_trang_thuc_te = fields.Selection([
        ('moi', 'Mới'),
        ('tot', 'Tốt'),
        ('binh_thuong', 'Bình thường'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hu_hong', 'Hư hỏng'),
    ], string='Tình trạng thực tế')
    vi_tri_thuc_te = fields.Selection([
        ('kho', 'Kho'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Bảo trì'),
        ('dang_chuyen_giao', 'Đang chuyển giao'),
    ], string='Vị trí thực tế')
    
    # Kết quả kiểm kê
    ket_qua = fields.Selection([
        ('khop', 'Khớp'),
        ('lech', 'Lệch thông tin'),
        ('thieu', 'Thiếu'),
        ('thua', 'Thừa'),
    ], string='Kết quả', compute='_compute_ket_qua', store=True)
    
    ghi_chu_kiem_ke = fields.Text(string='Ghi chú')
    nguoi_kiem_ke_id = fields.Many2one('nhan_vien', string='Người kiểm kê')
    ngay_kiem_ke = fields.Date(string='Ngày kiểm kê', default=fields.Date.today)

    @api.depends('co_thuc_te', 'tinh_trang_so_sach', 'tinh_trang_thuc_te', 
                 'vi_tri_so_sach', 'vi_tri_thuc_te', 'gia_tri_so_sach', 'gia_tri_thuc_te')
    def _compute_ket_qua(self):
        """Tự động xác định kết quả kiểm kê"""
        for record in self:
            if not record.co_thuc_te:
                record.ket_qua = 'thieu'
            elif (record.tinh_trang_so_sach == record.tinh_trang_thuc_te and 
                  record.vi_tri_so_sach == record.vi_tri_thuc_te and
                  abs(record.gia_tri_so_sach - record.gia_tri_thuc_te) < 0.01):
                record.ket_qua = 'khop'
            else:
                record.ket_qua = 'lech'

    @api.onchange('co_thuc_te')
    def _onchange_co_thuc_te(self):
        """Tự động điền thông tin thực tế từ sổ sách khi có thực tế"""
        if self.co_thuc_te:
            self.gia_tri_thuc_te = self.gia_tri_so_sach
            self.tinh_trang_thuc_te = self.tinh_trang_so_sach
            self.vi_tri_thuc_te = self.vi_tri_so_sach
        else:
            self.gia_tri_thuc_te = 0
            self.tinh_trang_thuc_te = False
            self.vi_tri_thuc_te = False

    def action_xac_nhan_khop(self):
        """Xác nhận khớp nhanh"""
        for record in self:
            # Lấy nhân viên hiện tại (nếu có)
            nhan_vien_id = False
            if hasattr(self.env.user, 'nhan_vien_id'):
                nhan_vien_id = self.env.user.nhan_vien_id.id if self.env.user.nhan_vien_id else False
            
            record.write({
                'co_thuc_te': True,
                'gia_tri_thuc_te': record.gia_tri_so_sach,
                'tinh_trang_thuc_te': record.tinh_trang_so_sach,
                'vi_tri_thuc_te': record.vi_tri_so_sach,
                'nguoi_kiem_ke_id': nhan_vien_id,
                'ngay_kiem_ke': fields.Date.today()
            })
