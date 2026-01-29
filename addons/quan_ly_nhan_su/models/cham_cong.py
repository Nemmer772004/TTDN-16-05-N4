# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Quản lý chấm công'
    _order = 'ngay_cham desc, gio_vao desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Mã chấm công', readonly=True, default='New')
    active = fields.Boolean(string='Active', default=True)
    
    # Thông tin nhân viên
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True, 
                                    tracking=True, ondelete='cascade')
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string='Mã NV', store=True)
    don_vi_id = fields.Many2one('don_vi', string='Đơn vị', 
                                related='nhan_vien_id.lich_su_cong_tac_ids.don_vi_id', 
                                store=True)
    
    # Thời gian chấm
    ngay_cham = fields.Date(string='Ngày chấm công', required=True, 
                            default=fields.Date.today, tracking=True)
    gio_vao = fields.Datetime(string='Giờ vào', tracking=True)
    gio_ra = fields.Datetime(string='Giờ ra', tracking=True)
    
    # Giờ làm việc chuẩn
    gio_vao_chuan = fields.Float(string='Giờ vào chuẩn', default=8.0,
                                  help='Giờ vào làm chuẩn (VD: 8h = 8.0)')
    gio_ra_chuan = fields.Float(string='Giờ ra chuẩn', default=17.0,
                                 help='Giờ ra làm chuẩn (VD: 17h = 17.0)')
    gio_lam_chuan = fields.Float(string='Giờ làm chuẩn/ngày', default=8.0)
    gio_nghi_trua = fields.Float(string='Giờ nghỉ trưa', default=1.0,
                                 help='Số giờ nghỉ trưa (VD: 1 giờ = 1.0)')
    
    # Tính toán
    tong_gio_lam = fields.Float(string='Tổng giờ làm', compute='_compute_gio_lam', store=True)
    gio_tang_ca = fields.Float(string='Giờ tăng ca', compute='_compute_gio_tang_ca', store=True)
    phut_tre = fields.Float(string='Phút đi trễ', compute='_compute_phut_tre', store=True)
    phut_ve_som = fields.Float(string='Phút về sớm', compute='_compute_phut_ve_som', store=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('dung_gio', 'Đúng giờ'),
        ('tre', 'Đi trễ'),
        ('som', 'Về sớm'),
        ('tre_va_som', 'Trễ và về sớm'),
        ('vang_mat', 'Vắng mặt'),
        ('nghi_phep', 'Nghỉ phép'),
        ('tang_ca', 'Tăng ca'),
    ], string='Trạng thái', compute='_compute_trang_thai', store=True, tracking=True)
    
    # Ghi chú
    ghi_chu = fields.Text(string='Ghi chú')
    ly_do_vang = fields.Text(string='Lý do vắng mặt')
    
    # Phê duyệt
    can_phe_duyet = fields.Boolean(string='Cần phê duyệt', default=False)
    da_phe_duyet = fields.Boolean(string='Đã phê duyệt', default=False, tracking=True)
    nguoi_phe_duyet_id = fields.Many2one('res.users', string='Người phê duyệt', readonly=True)
    ngay_phe_duyet = fields.Datetime(string='Ngày phê duyệt', readonly=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cham_cong') or 'New'
        return super(ChamCong, self).create(vals)
    
    @api.depends('gio_vao', 'gio_ra', 'gio_nghi_trua')
    def _compute_gio_lam(self):
        for record in self:
            if record.gio_vao and record.gio_ra:
                if record.gio_ra < record.gio_vao:
                    raise ValidationError('Giờ ra phải sau giờ vào!')
                delta = record.gio_ra - record.gio_vao
                # Trừ đi giờ nghỉ trưa
                total_hours = (delta.total_seconds() / 3600) - record.gio_nghi_trua
                record.tong_gio_lam = max(0, total_hours)
            else:
                record.tong_gio_lam = 0.0
    
    @api.depends('tong_gio_lam', 'gio_lam_chuan')
    def _compute_gio_tang_ca(self):
        for record in self:
            if record.tong_gio_lam > record.gio_lam_chuan:
                record.gio_tang_ca = record.tong_gio_lam - record.gio_lam_chuan
            else:
                record.gio_tang_ca = 0.0
    
    @api.depends('gio_vao', 'gio_vao_chuan')
    def _compute_phut_tre(self):
        for record in self:
            if record.gio_vao:
                gio_vao_actual = record.gio_vao.hour + record.gio_vao.minute / 60.0
                if gio_vao_actual > record.gio_vao_chuan:
                    record.phut_tre = (gio_vao_actual - record.gio_vao_chuan) * 60
                else:
                    record.phut_tre = 0.0
            else:
                record.phut_tre = 0.0
    
    @api.depends('gio_ra', 'gio_ra_chuan')
    def _compute_phut_ve_som(self):
        for record in self:
            if record.gio_ra:
                gio_ra_actual = record.gio_ra.hour + record.gio_ra.minute / 60.0
                if gio_ra_actual < record.gio_ra_chuan:
                    record.phut_ve_som = (record.gio_ra_chuan - gio_ra_actual) * 60
                else:
                    record.phut_ve_som = 0.0
            else:
                record.phut_ve_som = 0.0
    
    @api.depends('phut_tre', 'phut_ve_som', 'gio_vao', 'gio_ra', 'gio_tang_ca')
    def _compute_trang_thai(self):
        for record in self:
            if not record.gio_vao and not record.gio_ra:
                record.trang_thai = 'vang_mat'
            elif record.phut_tre > 0 and record.phut_ve_som > 0:
                record.trang_thai = 'tre_va_som'
            elif record.phut_tre > 0:
                record.trang_thai = 'tre'
            elif record.phut_ve_som > 0:
                record.trang_thai = 'som'
            elif record.gio_tang_ca > 0:
                record.trang_thai = 'tang_ca'
            else:
                record.trang_thai = 'dung_gio'
    
    @api.constrains('ngay_cham', 'nhan_vien_id')
    def _check_duplicate(self):
        for record in self:
            existing = self.search([
                ('ngay_cham', '=', record.ngay_cham),
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('id', '!=', record.id),
            ])
            if existing:
                raise ValidationError(f'Nhân viên {record.nhan_vien_id.ho_va_ten} đã có bản ghi chấm công ngày {record.ngay_cham}!')
    
    def action_check_in(self):
        """Chấm công vào"""
        self.ensure_one()
        if self.gio_vao:
            raise ValidationError('Đã chấm công vào rồi!')
        self.gio_vao = fields.Datetime.now()
        self.message_post(body=f"Chấm công vào lúc {self.gio_vao}")
    
    def action_check_out(self):
        """Chấm công ra"""
        self.ensure_one()
        if not self.gio_vao:
            raise ValidationError('Chưa chấm công vào!')
        if self.gio_ra:
            raise ValidationError('Đã chấm công ra rồi!')
        self.gio_ra = fields.Datetime.now()
        self.message_post(body=f"Chấm công ra lúc {self.gio_ra}")
    
    def action_phe_duyet(self):
        """Phê duyệt chấm công"""
        self.ensure_one()
        self.write({
            'da_phe_duyet': True,
            'nguoi_phe_duyet_id': self.env.user.id,
            'ngay_phe_duyet': fields.Datetime.now(),
        })
        self.message_post(body=f"Đã phê duyệt bởi {self.env.user.name}")
    
    def action_gui_duyet(self):
        """Gửi phê duyệt"""
        self.ensure_one()
        self.can_phe_duyet = True
        self.message_post(body="Đã gửi yêu cầu phê duyệt")
