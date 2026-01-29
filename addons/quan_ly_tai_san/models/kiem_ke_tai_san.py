# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KiemKeTaiSan(models.Model):
    _name = 'kiem_ke_tai_san'
    _description = 'Kiểm kê tài sản'
    _order = 'ngay_kiem_ke desc'

    name = fields.Char(string='Mã phiếu kiểm kê', required=True, copy=False, default='Mới')
    
    tieu_de = fields.Char(string='Tiêu đề', required=True)
    ngay_kiem_ke = fields.Date(string='Ngày kiểm kê', required=True, default=fields.Date.today)
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu', required=True)
    ngay_ket_thuc = fields.Date(string='Ngày kết thúc')
    
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban kiểm kê')
    loai_tai_san = fields.Selection([
        ('thiet_bi_dien_tu', 'Thiết bị điện tử'),
        ('noi_that', 'Nội thất'),
        ('phuong_tien', 'Phương tiện'),
        ('thiet_bi_van_phong', 'Thiết bị văn phòng'),
        ('may_moc', 'Máy móc'),
        ('khac', 'Khác'),
    ], string='Loại tài sản kiểm kê')
    
    mo_ta = fields.Text(string='Mô tả')
    
    # Người phụ trách
    truong_doan_id = fields.Many2one('nhan_vien', string='Trưởng đoàn', required=True)
    thanh_vien_ids = fields.Many2many('nhan_vien', string='Thành viên')
    
    # Chi tiết kiểm kê
    chi_tiet_ids = fields.One2many('chi_tiet_kiem_ke', 'kiem_ke_id', string='Chi tiết kiểm kê')
    
    # Thống kê
    tong_so_tai_san = fields.Integer(string='Tổng số tài sản', compute='_compute_thong_ke', store=True)
    so_tai_san_khop = fields.Integer(string='Số tài sản khớp', compute='_compute_thong_ke', store=True)
    so_tai_san_lech = fields.Integer(string='Số tài sản lệch', compute='_compute_thong_ke', store=True)
    so_tai_san_thieu = fields.Integer(string='Số tài sản thiếu', compute='_compute_thong_ke', store=True)
    so_tai_san_thua = fields.Integer(string='Số tài sản thừa', compute='_compute_thong_ke', store=True)
    
    ty_le_khop = fields.Float(string='Tỷ lệ khớp (%)', compute='_compute_thong_ke', store=True)
    
    trang_thai = fields.Selection([
        ('du_thao', 'Dự thảo'),
        ('dang_kiem_ke', 'Đang kiểm kê'),
        ('hoan_thanh', 'Hoàn thành'),
        ('huy', 'Hủy'),
    ], string='Trạng thái', default='du_thao', required=True)
    
    ket_luan = fields.Text(string='Kết luận')
    bao_cao_file = fields.Binary(string='Báo cáo kiểm kê')
    ten_file = fields.Char(string='Tên file')
    ghi_chu = fields.Text(string='Ghi chú')

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_dates(self):
        """Kiểm tra ngày hợp lệ"""
        for record in self:
            if record.ngay_ket_thuc and record.ngay_bat_dau > record.ngay_ket_thuc:
                raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu!")

    @api.depends('chi_tiet_ids', 'chi_tiet_ids.ket_qua')
    def _compute_thong_ke(self):
        """Tính toán thống kê kiểm kê"""
        for record in self:
            chi_tiets = record.chi_tiet_ids
            record.tong_so_tai_san = len(chi_tiets)
            
            record.so_tai_san_khop = len(chi_tiets.filtered(lambda x: x.ket_qua == 'khop'))
            record.so_tai_san_lech = len(chi_tiets.filtered(lambda x: x.ket_qua == 'lech'))
            record.so_tai_san_thieu = len(chi_tiets.filtered(lambda x: x.ket_qua == 'thieu'))
            record.so_tai_san_thua = len(chi_tiets.filtered(lambda x: x.ket_qua == 'thua'))
            
            if record.tong_so_tai_san > 0:
                record.ty_le_khop = (record.so_tai_san_khop / record.tong_so_tai_san) * 100
            else:
                record.ty_le_khop = 0

    @api.model
    def create(self, vals):
        """Tạo mã kiểm kê tự động"""
        if vals.get('name', 'Mới') == 'Mới':
            vals['name'] = self.env['ir.sequence'].next_by_code('kiem_ke_tai_san.sequence') or 'Mới'
        return super(KiemKeTaiSan, self).create(vals)

    def action_bat_dau_kiem_ke(self):
        """Bắt đầu kiểm kê"""
        self.ensure_one()
        if self.trang_thai != 'du_thao':
            raise ValidationError("Chỉ phiếu kiểm kê ở trạng thái Dự thảo mới có thể bắt đầu!")
        
        # Tự động tạo chi tiết kiểm kê từ danh sách tài sản
        self._tao_chi_tiet_kiem_ke()
        
        self.write({
            'trang_thai': 'dang_kiem_ke',
            'ngay_bat_dau': fields.Date.today()
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_hoan_thanh_kiem_ke(self):
        """Hoàn thành kiểm kê"""
        self.ensure_one()
        if self.trang_thai != 'dang_kiem_ke':
            raise ValidationError("Chỉ phiếu kiểm kê đang thực hiện mới có thể hoàn thành!")
        
        self.write({
            'trang_thai': 'hoan_thanh',
            'ngay_ket_thuc': fields.Date.today()
        })
        
        # Tự động cập nhật trạng thái tài sản dựa trên kết quả kiểm kê
        self._cap_nhat_tai_san_sau_kiem_ke()
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_huy_kiem_ke(self):
        """Hủy kiểm kê"""
        self.ensure_one()
        self.write({'trang_thai': 'huy'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def _tao_chi_tiet_kiem_ke(self):
        """Tự động tạo danh sách chi tiết kiểm kê từ tài sản"""
        self.ensure_one()
        
        # Tìm tài sản theo điều kiện
        domain = [('tinh_trang', '!=', 'da_thanh_ly')]
        
        if self.phong_ban_id:
            domain.append(('phong_ban_id', '=', self.phong_ban_id.id))
        if self.loai_tai_san:
            domain.append(('loai_tai_san', '=', self.loai_tai_san))
        
        tai_sans = self.env['tai_san'].search(domain)
        
        # Tạo chi tiết kiểm kê cho từng tài sản
        ChiTietKiemKe = self.env['chi_tiet_kiem_ke']
        for tai_san in tai_sans:
            ChiTietKiemKe.create({
                'kiem_ke_id': self.id,
                'tai_san_id': tai_san.id,
                'gia_tri_so_sach': tai_san.gia_tri,
                'tinh_trang_so_sach': tai_san.tinh_trang,
                'vi_tri_so_sach': tai_san.vi_tri,
            })

    def _cap_nhat_tai_san_sau_kiem_ke(self):
        """Cập nhật trạng thái tài sản sau kiểm kê"""
        self.ensure_one()
        
        for chi_tiet in self.chi_tiet_ids:
            if chi_tiet.ket_qua == 'thieu':
                # Đánh dấu tài sản bị mất
                chi_tiet.tai_san_id.write({
                    'tinh_trang': 'hu_hong',
                    'ghi_chu': f"Mất theo phiếu kiểm kê {self.name}"
                })
            elif chi_tiet.ket_qua == 'lech' and chi_tiet.tinh_trang_thuc_te:
                # Cập nhật trạng thái thực tế
                chi_tiet.tai_san_id.write({
                    'tinh_trang': chi_tiet.tinh_trang_thuc_te
                })
