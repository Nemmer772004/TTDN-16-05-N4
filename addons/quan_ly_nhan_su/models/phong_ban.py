# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PhongBan(models.Model):
    """
    Model alias cho DonVi - để tương thích với các module khác
    sử dụng tên 'phong_ban' thay vì 'don_vi'
    
    Sử dụng _inherits để kế thừa delegation:
    - Mọi field của don_vi tự động có trong phong_ban
    - Không cần định nghĩa lại các field
    """
    _name = 'phong_ban'
    _description = 'Phòng ban (Alias cho Đơn vị)'
    _inherits = {'don_vi': 'don_vi_id'}
    _rec_name = 'ten_don_vi'  # Dùng field từ don_vi

    don_vi_id = fields.Many2one(
        'don_vi', 
        string='Đơn vị', 
        required=True, 
        ondelete='cascade', 
        auto_join=True
    )

    @api.model
    def create(self, vals):
        """
        Override create để tự động generate ma_don_vi nếu chưa có
        """
        # Nếu không có ma_don_vi, tạo tự động từ sequence hoặc ten_don_vi
        if 'ma_don_vi' not in vals or not vals.get('ma_don_vi'):
            if vals.get('ten_don_vi'):
                # Tạo mã từ tên (viết tắt)
                ten = vals['ten_don_vi'].strip()
                words = ten.split()
                if len(words) > 1:
                    # Lấy chữ cái đầu của mỗi từ
                    ma = ''.join([w[0].upper() for w in words])
                else:
                    # Lấy 3 ký tự đầu
                    ma = ten[:3].upper()
                
                # Thêm số thứ tự nếu trùng
                base_ma = ma
                counter = 1
                while self.env['don_vi'].search([('ma_don_vi', '=', ma)], limit=1):
                    ma = f"{base_ma}{counter}"
                    counter += 1
                
                vals['ma_don_vi'] = ma
            else:
                # Fallback: dùng PB + số thứ tự
                last_id = self.env['don_vi'].search([], order='id desc', limit=1)
                next_num = (last_id.id if last_id else 0) + 1
                vals['ma_don_vi'] = f"PB{next_num:03d}"
        
        return super(PhongBan, self).create(vals)
