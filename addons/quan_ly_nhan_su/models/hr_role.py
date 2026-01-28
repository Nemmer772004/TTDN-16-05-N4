# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrRole(models.Model):
    _name = 'hr.role'
    _description = 'Vai trò nghiệp vụ nhân sự'
    _rec_name = 'ten_vai_tro'

    ma_vai_tro = fields.Char("Mã vai trò", required=True)
    ten_vai_tro = fields.Char("Tên vai trò", required=True)
    mo_ta = fields.Text("Mô tả vai trò")
    loai_vai_tro = fields.Selection([
        ('nhan_vien', 'Nhân viên thường'),
        ('truong_don_vi', 'Trưởng đơn vị'),
        ('quan_ly_tai_san', 'Quản lý tài sản'),
        ('ky_thuat', 'Nhân viên kỹ thuật/bảo trì'),
        ('quan_tri', 'Quản trị hệ thống'),
    ], string="Loại vai trò", default='nhan_vien', required=True)
    
    nhan_vien_ids = fields.Many2many('nhan_vien', 'nhan_vien_hr_role_rel', 
                                      'role_id', 'nhan_vien_id', 
                                      string="Nhân viên")
    so_luong_nhan_vien = fields.Integer("Số lượng nhân viên", 
                                         compute="_compute_so_luong_nhan_vien",
                                         store=True)
    
    _sql_constraints = [
        ('ma_vai_tro_unique', 'unique(ma_vai_tro)', 'Mã vai trò phải là duy nhất')
    ]
    
    @api.depends('nhan_vien_ids')
    def _compute_so_luong_nhan_vien(self):
        for record in self:
            record.so_luong_nhan_vien = len(record.nhan_vien_ids)
