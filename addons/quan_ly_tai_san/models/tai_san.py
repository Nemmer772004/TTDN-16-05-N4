# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class TaiSan(models.Model):
    _name = 'tai_san'
    _description = 'Quản lý Tài sản'
    _order = 'ma_tai_san desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin cơ bản
    ma_tai_san = fields.Char(
        string='Mã tài sản',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: 'New'
    )
    name = fields.Char(string='Tên tài sản', required=True, tracking=True)
    ten_tai_san = fields.Char(related='name', string='Tên tài sản', readonly=True, store=True)
    
    loai_tai_san = fields.Selection([
        ('thiet_bi_dien_tu', 'Thiết bị điện tử'),
        ('noi_that', 'Nội thất'),
        ('phuong_tien', 'Phương tiện'),
        ('thiet_bi_van_phong', 'Thiết bị văn phòng'),
        ('may_moc', 'Máy móc'),
        ('khac', 'Khác'),
    ], string='Loại tài sản', required=True, tracking=True)
    
    # Thông tin tài chính
    gia_tri = fields.Float(string='Giá trị (VNĐ)', required=True, tracking=True)
    gia_tri_mua = fields.Float(related='gia_tri', string='Giá trị mua (VNĐ)', readonly=True, store=True)
    ngay_mua = fields.Date(string='Ngày mua', required=True, default=fields.Date.today, tracking=True)
    thoi_gian_khau_hao = fields.Integer(string='Thời gian khấu hao (năm)', default=5, help='Số năm khấu hao tài sản')
    gia_tri_khau_hao_hang_thang = fields.Float(
        string='Khấu hao hàng tháng',
        compute='_compute_khau_hao',
        store=True
    )
    gia_tri_con_lai = fields.Float(
        string='Giá trị còn lại',
        compute='_compute_khau_hao',
        store=True
    )
    
    # Trạng thái
    tinh_trang = fields.Selection([
        ('moi', 'Mới 100%'),
        ('tot', 'Đang sử dụng tốt'),
        ('trung_binh', 'Đang sử dụng (có vấn đề nhỏ)'),
        ('can_bao_tri', 'Cần bảo trì'),
        ('hong', 'Hỏng'),
        ('cho_thanh_ly', 'Chờ thanh lý'),
        ('da_thanh_ly', 'Đã thanh lý'),
    ], string='Tình trạng', default='moi', required=True, tracking=True)
    
    vi_tri = fields.Selection([
        ('kho', 'Kho'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Bảo trì'),
        ('thanh_ly', 'Thanh lý'),
    ], string='Vị trí', default='kho', required=True, tracking=True)
    
    # Thông tin chi tiết
    mo_ta = fields.Text(string='Mô tả chi tiết')
    ghi_chu = fields.Text(string='Ghi chú')
    hinh_anh = fields.Binary(string='Hình ảnh')
    
    # LIÊN KẾT VỚI MODULE KHÁC
    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        tracking=True,
        help='Phòng ban đang quản lý/sử dụng tài sản'
    )
    nguoi_quan_ly_id = fields.Many2one(
        'nhan_vien',
        string='Người quản lý',
        tracking=True,
        help='Nhân viên chịu trách nhiệm quản lý tài sản này'
    )
    phong_hop_id = fields.Many2one(
        'quan_ly_phong_hop',
        string='Phòng họp',
        tracking=True,
        help='Chỉ áp dụng cho thiết bị phòng họp'
    )
    
    # QUAN HỆ ONE2MANY
    lich_su_su_dung_ids = fields.One2many(
        'lich_su_su_dung_tai_san',
        'tai_san_id',
        string='Lịch sử sử dụng'
    )
    lich_su_bao_tri_ids = fields.One2many(
        'bao_tri_tai_san',
        'tai_san_id',
        string='Lịch sử bảo trì'
    )
    lich_su_chuyen_giao_ids = fields.One2many(
        'chuyen_giao_tai_san',
        'tai_san_id',
        string='Lịch sử chuyển giao'
    )
    
    # Computed fields
    so_lan_bao_tri = fields.Integer(
        string='Số lần bảo trì',
        compute='_compute_so_lan_bao_tri'
    )
    tong_chi_phi_bao_tri = fields.Float(
        string='Tổng chi phí bảo trì',
        compute='_compute_tong_chi_phi_bao_tri'
    )
    nguoi_dang_su_dung = fields.Many2one(
        'nhan_vien',
        string='Người đang sử dụng',
        compute='_compute_nguoi_dang_su_dung'
    )

    @api.model
    def create(self, vals):
        """Tự động tạo mã tài sản"""
        if vals.get('ma_tai_san', 'New') == 'New':
            vals['ma_tai_san'] = self.env['ir.sequence'].next_by_code('tai_san.sequence') or 'New'
        return super(TaiSan, self).create(vals)

    def write(self, vals):
        """Tự động tạo lịch sử sử dụng khi vi_tri đổi sang 'dang_su_dung'"""
        result = super(TaiSan, self).write(vals)
        
        # Nếu vị trí đổi thành "Đang sử dụng"
        if vals.get('vi_tri') == 'dang_su_dung':
            for record in self:
                # Kiểm tra xem có lịch sử đang sử dụng chưa hoàn thành không
                lich_su_dang_mo = record.lich_su_su_dung_ids.filtered(lambda r: r.trang_thai == 'dang_su_dung')
                
                # Chỉ tạo mới nếu chưa có lịch sử đang mở
                if not lich_su_dang_mo:
                    # Tạo lịch sử sử dụng mới
                    self.env['lich_su_su_dung_tai_san'].create({
                        'tai_san_id': record.id,
                        'nguoi_su_dung_id': record.nguoi_quan_ly_id.id if record.nguoi_quan_ly_id else False,
                        'phong_ban_id': record.phong_ban_id.id if record.phong_ban_id else False,
                        'ngay_bat_dau': fields.Date.today(),
                        'trang_thai': 'dang_su_dung',
                    })
        
        # Nếu vị trí đổi về "Kho" → tự động trả tài sản
        elif vals.get('vi_tri') == 'kho':
            for record in self:
                # Tìm các lịch sử đang sử dụng và đóng lại
                lich_su_dang_mo = record.lich_su_su_dung_ids.filtered(lambda r: r.trang_thai == 'dang_su_dung')
                for lich_su in lich_su_dang_mo:
                    lich_su.write({
                        'trang_thai': 'da_tra',
                        'ngay_ket_thuc': fields.Date.today(),
                    })
        
        return result

    @api.depends('gia_tri', 'ngay_mua', 'thoi_gian_khau_hao')
    def _compute_khau_hao(self):
        """Tính toán khấu hao tài sản"""
        for record in self:
            if record.thoi_gian_khau_hao > 0:
                # Khấu hao hàng tháng
                record.gia_tri_khau_hao_hang_thang = record.gia_tri / (record.thoi_gian_khau_hao * 12)
                
                # Tính số tháng đã sử dụng
                if record.ngay_mua:
                    today = date.today()
                    months_used = (today.year - record.ngay_mua.year) * 12 + (today.month - record.ngay_mua.month)
                    
                    # Giá trị đã khấu hao
                    gia_tri_da_khau_hao = record.gia_tri_khau_hao_hang_thang * months_used
                    
                    # Giá trị còn lại (không âm)
                    record.gia_tri_con_lai = max(0, record.gia_tri - gia_tri_da_khau_hao)
                else:
                    record.gia_tri_con_lai = record.gia_tri
            else:
                record.gia_tri_khau_hao_hang_thang = 0
                record.gia_tri_con_lai = record.gia_tri

    @api.depends('lich_su_bao_tri_ids')
    def _compute_so_lan_bao_tri(self):
        """Đếm số lần bảo trì"""
        for record in self:
            record.so_lan_bao_tri = len(record.lich_su_bao_tri_ids.filtered(lambda r: r.trang_thai == 'hoan_thanh'))

    @api.depends('lich_su_bao_tri_ids.chi_phi')
    def _compute_tong_chi_phi_bao_tri(self):
        """Tính tổng chi phí bảo trì"""
        for record in self:
            record.tong_chi_phi_bao_tri = sum(record.lich_su_bao_tri_ids.mapped('chi_phi'))

    @api.depends('lich_su_su_dung_ids.trang_thai')
    def _compute_nguoi_dang_su_dung(self):
        """Tìm người đang sử dụng tài sản"""
        for record in self:
            dang_su_dung = record.lich_su_su_dung_ids.filtered(lambda r: r.trang_thai == 'dang_su_dung')
            record.nguoi_dang_su_dung = dang_su_dung[0].nguoi_su_dung_id if dang_su_dung else False

    def action_cap_nhat_tinh_trang(self):
        """Mở wizard cập nhật tình trạng"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cập nhật tình trạng',
            'res_model': 'tai_san',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_bao_tri(self):
        """Tạo phiếu bảo trì mới"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tạo phiếu bảo trì',
            'res_model': 'bao_tri_tai_san',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tai_san_id': self.id,
            }
        }

    def action_chuyen_giao(self):
        """Tạo phiếu chuyển giao"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chuyển giao tài sản',
            'res_model': 'chuyen_giao_tai_san',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tai_san_id': self.id,
                'default_tu_phong_ban_id': self.phong_ban_id.id,
                'default_tu_nguoi_id': self.nguoi_quan_ly_id.id,
            }
        }
