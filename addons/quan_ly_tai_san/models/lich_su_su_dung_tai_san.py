# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class LichSuSuDungTaiSan(models.Model):
    _name = 'lich_su_su_dung_tai_san'
    _description = 'Lịch sử sử dụng tài sản'
    _order = 'ngay_bat_dau desc'

    name = fields.Char(string='Mã phiếu', compute='_compute_name', store=True)
    
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', required=True, ondelete='cascade')
    ma_tai_san = fields.Char(related='tai_san_id.ma_tai_san', string='Mã tài sản', readonly=True)
    
    nguoi_su_dung_id = fields.Many2one('nhan_vien', string='Người sử dụng', required=True)
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban')
    
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu', required=True, default=fields.Date.today)
    ngay_ket_thuc = fields.Date(string='Ngày kết thúc')
    
    trang_thai = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('da_tra', 'Đã trả'),
    ], string='Trạng thái', default='dang_su_dung', required=True)
    
    ly_do = fields.Text(string='Lý do sử dụng')
    ghi_chu = fields.Text(string='Ghi chú')

    @api.depends('tai_san_id', 'nguoi_su_dung_id')
    def _compute_name(self):
        """Tạo tên tự động"""
        for record in self:
            if record.tai_san_id and record.nguoi_su_dung_id:
                record.name = f"SD-{record.tai_san_id.ma_tai_san}-{record.nguoi_su_dung_id.ho_va_ten}"
            else:
                record.name = "Mới"

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_dates(self):
        """Kiểm tra ngày bắt đầu phải trước ngày kết thúc"""
        for record in self:
            if record.ngay_ket_thuc and record.ngay_bat_dau > record.ngay_ket_thuc:
                raise exceptions.ValidationError('Ngày bắt đầu phải trước ngày kết thúc!')

    @api.model
    def create(self, vals):
        """Cập nhật trạng thái tài sản khi tạo mới"""
        result = super(LichSuSuDungTaiSan, self).create(vals)
        if result.trang_thai == 'dang_su_dung':
            result.tai_san_id.write({
                'vi_tri': 'dang_su_dung',
                'phong_ban_id': result.phong_ban_id.id,
                'nguoi_quan_ly_id': result.nguoi_su_dung_id.id,
            })
        return result

    def write(self, vals):
        """Cập nhật trạng thái tài sản khi thay đổi"""
        result = super(LichSuSuDungTaiSan, self).write(vals)
        for record in self:
            if record.trang_thai == 'da_tra':
                record.tai_san_id.write({'vi_tri': 'kho'})
        return result

    def action_tra_tai_san(self):
        """Trả tài sản"""
        self.ensure_one()
        self.write({
            'trang_thai': 'da_tra',
            'ngay_ket_thuc': fields.Date.today(),
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}
