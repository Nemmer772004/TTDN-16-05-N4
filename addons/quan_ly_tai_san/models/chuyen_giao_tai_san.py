# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ChuyenGiaoTaiSan(models.Model):
    _name = 'chuyen_giao_tai_san'
    _description = 'Chuyển giao tài sản'
    _order = 'ngay_chuyen_giao desc'

    name = fields.Char(string='Mã chuyển giao', compute='_compute_name', store=True)
    
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', required=True, ondelete='cascade')
    ma_tai_san = fields.Char(related='tai_san_id.ma_tai_san', string='Mã tài sản', readonly=True)
    
    loai_chuyen_giao = fields.Selection([
        ('phong_ban', 'Chuyển phòng ban'),
        ('nguoi_dung', 'Chuyển người dùng'),
        ('vi_tri', 'Chuyển vị trí'),
    ], string='Loại chuyển giao', required=True, default='phong_ban')
    
    # Thông tin nguồn (từ)
    tu_phong_ban_id = fields.Many2one('phong_ban', string='Từ phòng ban')
    tu_nguoi_dung_id = fields.Many2one('nhan_vien', string='Từ người dùng')
    tu_phong_hop_id = fields.Many2one('quan_ly_phong_hop', string='Từ phòng họp')
    
    # Thông tin đích (đến)
    den_phong_ban_id = fields.Many2one('phong_ban', string='Đến phòng ban')
    den_nguoi_dung_id = fields.Many2one('nhan_vien', string='Đến người dùng')
    den_phong_hop_id = fields.Many2one('quan_ly_phong_hop', string='Đến phòng họp')
    
    ngay_chuyen_giao = fields.Date(string='Ngày chuyển giao', required=True, default=fields.Date.today)
    ngay_giao_hang = fields.Date(string='Ngày giao hàng thực tế')
    
    ly_do = fields.Text(string='Lý do chuyển giao', required=True)
    ghi_chu = fields.Text(string='Ghi chú')
    
    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('dang_chuyen', 'Đang chuyển'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tu_choi', 'Từ chối'),
    ], string='Trạng thái', default='cho_duyet', required=True)
    
    nguoi_de_xuat_id = fields.Many2one(
        'res.users', 
        string='Người đề xuất', 
        default=lambda self: self.env.user,
        readonly=True
    )
    nguoi_duyet_id = fields.Many2one('res.users', string='Người duyệt')
    ngay_duyet = fields.Date(string='Ngày duyệt', readonly=True)
    
    file_dinh_kem = fields.Binary(string='Biên bản bàn giao')
    ten_file = fields.Char(string='Tên file')

    @api.depends('tai_san_id', 'ngay_chuyen_giao')
    def _compute_name(self):
        """Tạo mã chuyển giao tự động"""
        for record in self:
            if record.tai_san_id and record.ngay_chuyen_giao:
                record.name = f"CG-{record.tai_san_id.ma_tai_san}-{record.ngay_chuyen_giao.strftime('%Y%m%d')}"
            else:
                record.name = "Mới"

    @api.constrains('loai_chuyen_giao', 'tu_phong_ban_id', 'den_phong_ban_id', 
                    'tu_nguoi_dung_id', 'den_nguoi_dung_id', 'tu_phong_hop_id', 'den_phong_hop_id')
    def _check_chuyen_giao_valid(self):
        """Kiểm tra thông tin chuyển giao hợp lệ"""
        for record in self:
            if record.loai_chuyen_giao == 'phong_ban':
                if not record.tu_phong_ban_id or not record.den_phong_ban_id:
                    raise ValidationError("Vui lòng chọn phòng ban nguồn và đích!")
                if record.tu_phong_ban_id == record.den_phong_ban_id:
                    raise ValidationError("Phòng ban nguồn và đích không được giống nhau!")
            
            elif record.loai_chuyen_giao == 'nguoi_dung':
                if not record.tu_nguoi_dung_id or not record.den_nguoi_dung_id:
                    raise ValidationError("Vui lòng chọn người dùng nguồn và đích!")
                if record.tu_nguoi_dung_id == record.den_nguoi_dung_id:
                    raise ValidationError("Người dùng nguồn và đích không được giống nhau!")

    @api.model
    def create(self, vals):
        """Tự động điền thông tin nguồn từ tài sản"""
        if vals.get('tai_san_id'):
            tai_san = self.env['tai_san'].browse(vals['tai_san_id'])
            
            # Nếu chưa có thông tin nguồn, lấy từ tài sản hiện tại
            if not vals.get('tu_phong_ban_id') and tai_san.phong_ban_id:
                vals['tu_phong_ban_id'] = tai_san.phong_ban_id.id
            if not vals.get('tu_nguoi_dung_id') and tai_san.nguoi_quan_ly_id:
                vals['tu_nguoi_dung_id'] = tai_san.nguoi_quan_ly_id.id
            if not vals.get('tu_phong_hop_id') and tai_san.phong_hop_id:
                vals['tu_phong_hop_id'] = tai_san.phong_hop_id.id
        
        return super(ChuyenGiaoTaiSan, self).create(vals)

    def action_duyet(self):
        """Phê duyệt chuyển giao"""
        self.ensure_one()
        self.write({
            'trang_thai': 'da_duyet',
            'nguoi_duyet_id': self.env.user.id,
            'ngay_duyet': fields.Date.today()
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_tu_choi(self):
        """Từ chối chuyển giao"""
        self.ensure_one()
        self.write({
            'trang_thai': 'tu_choi',
            'nguoi_duyet_id': self.env.user.id,
            'ngay_duyet': fields.Date.today()
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_bat_dau_chuyen(self):
        """Bắt đầu chuyển giao"""
        self.ensure_one()
        if self.trang_thai != 'da_duyet':
            raise ValidationError("Chỉ chuyển giao đã được duyệt mới có thể bắt đầu!")
        
        self.write({'trang_thai': 'dang_chuyen'})
        self.tai_san_id.write({'vi_tri': 'dang_chuyen_giao'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_hoan_thanh(self):
        """Hoàn thành chuyển giao"""
        self.ensure_one()
        if self.trang_thai != 'dang_chuyen':
            raise ValidationError("Chỉ chuyển giao đang thực hiện mới có thể hoàn thành!")
        
        # Cập nhật thông tin tài sản theo loại chuyển giao
        tai_san_vals = {'vi_tri': 'dang_su_dung'}
        
        if self.loai_chuyen_giao == 'phong_ban' and self.den_phong_ban_id:
            tai_san_vals['phong_ban_id'] = self.den_phong_ban_id.id
        
        if self.loai_chuyen_giao == 'nguoi_dung' and self.den_nguoi_dung_id:
            tai_san_vals['nguoi_quan_ly_id'] = self.den_nguoi_dung_id.id
        
        if self.den_phong_hop_id:
            tai_san_vals['phong_hop_id'] = self.den_phong_hop_id.id
        
        self.tai_san_id.write(tai_san_vals)
        self.write({
            'trang_thai': 'hoan_thanh',
            'ngay_giao_hang': fields.Date.today()
        })
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}
