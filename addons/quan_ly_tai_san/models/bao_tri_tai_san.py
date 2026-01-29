# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class BaoTriTaiSan(models.Model):
    _name = 'bao_tri_tai_san'
    _description = 'Bảo trì tài sản'
    _order = 'ngay_bao_tri desc'

    name = fields.Char(string='Mã phiếu bảo trì', compute='_compute_name', store=True)
    
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', required=True, ondelete='cascade')
    ma_tai_san = fields.Char(related='tai_san_id.ma_tai_san', string='Mã tài sản', readonly=True)
    
    loai_bao_tri = fields.Selection([
        ('dinh_ky', 'Bảo trì định kỳ'),
        ('sua_chua', 'Sửa chữa'),
        ('nang_cap', 'Nâng cấp'),
    ], string='Loại bảo trì', required=True, default='sua_chua')
    
    ngay_bao_tri = fields.Date(string='Ngày bảo trì', required=True, default=fields.Date.today)
    nguoi_thuc_hien = fields.Many2one('nhan_vien', string='Đơn vị/Người thực hiện', required=True)
    chi_phi = fields.Float(string='Chi phí (VNĐ)', default=0)
    
    mo_ta_van_de = fields.Text(string='Mô tả vấn đề')
    ket_qua = fields.Text(string='Kết quả bảo trì')
    
    trang_thai = fields.Selection([
        ('ke_hoach', 'Đã lên kế hoạch'),
        ('dang_bao_tri', 'Đang bảo trì'),
        ('hoan_thanh', 'Hoàn thành'),
    ], string='Trạng thái', default='ke_hoach', required=True)
    
    ngay_bao_tri_tiep_theo = fields.Date(
        string='Ngày bảo trì tiếp theo (dự kiến)',
        compute='_compute_ngay_bao_tri_tiep_theo',
        store=True,
        help='Tự động tính 6 tháng kể từ ngày bảo trì'
    )
    
    file_dinh_kem = fields.Binary(string='File đính kèm')
    ten_file = fields.Char(string='Tên file')
    ghi_chu = fields.Text(string='Ghi chú')

    @api.depends('tai_san_id', 'ngay_bao_tri')
    def _compute_name(self):
        """Tạo mã phiếu tự động"""
        for record in self:
            if record.tai_san_id and record.ngay_bao_tri:
                record.name = f"BT-{record.tai_san_id.ma_tai_san}-{record.ngay_bao_tri.strftime('%Y%m%d')}"
            else:
                record.name = "Mới"

    @api.depends('ngay_bao_tri', 'loai_bao_tri')
    def _compute_ngay_bao_tri_tiep_theo(self):
        """Tính ngày bảo trì tiếp theo (6 tháng sau)"""
        for record in self:
            if record.ngay_bao_tri and record.loai_bao_tri == 'dinh_ky':
                record.ngay_bao_tri_tiep_theo = record.ngay_bao_tri + relativedelta(months=6)
            else:
                record.ngay_bao_tri_tiep_theo = False

    @api.model
    def create(self, vals):
        """Cập nhật trạng thái tài sản khi tạo bảo trì"""
        result = super(BaoTriTaiSan, self).create(vals)
        if result.trang_thai == 'dang_bao_tri':
            result.tai_san_id.write({
                'vi_tri': 'bao_tri',
                'tinh_trang': 'can_bao_tri'
            })
        return result

    def write(self, vals):
        """Cập nhật trạng thái tài sản khi hoàn thành bảo trì"""
        result = super(BaoTriTaiSan, self).write(vals)
        for record in self:
            if record.trang_thai == 'hoan_thanh':
                record.tai_san_id.write({
                    'vi_tri': 'kho',
                    'tinh_trang': 'tot'
                })
        return result

    def action_bat_dau_bao_tri(self):
        """Bắt đầu bảo trì"""
        self.ensure_one()
        self.write({'trang_thai': 'dang_bao_tri'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_hoan_thanh_bao_tri(self):
        """Hoàn thành bảo trì"""
        self.ensure_one()
        self.write({'trang_thai': 'hoan_thanh'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def canh_bao_bao_tri_dinh_ky(self):
        """Cron job: Gửi cảnh báo bảo trì định kỳ"""
        # Tìm các bảo trì đã hoàn thành và sắp đến hạn bảo trì tiếp theo (trong 7 ngày)
        today = fields.Date.today()
        threshold = today + relativedelta(days=7)
        
        bao_tri_sap_den = self.search([
            ('trang_thai', '=', 'hoan_thanh'),
            ('ngay_bao_tri_tiep_theo', '<=', threshold),
            ('ngay_bao_tri_tiep_theo', '>=', today)
        ])
        
        # TODO: Gửi email/thông báo cho người quản lý tài sản
        for record in bao_tri_sap_den:
            pass  # Có thể implement gửi email sau
