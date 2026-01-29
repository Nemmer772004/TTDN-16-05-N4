# -*- coding: utf-8 -*-
{
    'name': "Quản lý Nhân sự",

    'summary': """
        Quản lý nhân sự toàn diện với chấm công, nghỉ phép, 
        vai trò nghiệp vụ, phân quyền và quản lý tài sản""",

    'description': """
        Module quản lý nhân sự mở rộng bao gồm:
        - Quản lý thông tin nhân viên, phòng ban, chức vụ
        - ⭐ Chấm công tự động với tính toán giờ làm, tăng ca
        - ⭐ Quản lý nghỉ phép với workflow phê duyệt
        - Quản lý vai trò nghiệp vụ (HR Role)
        - Trạng thái làm việc và phân quyền
        - Quản lý trưởng đơn vị và phê duyệt
        - Quyền đặt phòng họp với hạn mức
        - Tham gia cuộc họp
        - Phân công tài sản
        - Mượn trả thiết bị với workflow
        - Nhật ký sử dụng tài nguyên
        - Quản lý vi phạm nhân sự
        - Báo cáo và thống kê toàn diện
    """,

    'author': "Nhóm 4 - TTDN-16-05-N4",
    'website': "https://github.com/Nemmer772004/TTDN-16-05-N4",

    'category': 'Human Resources',
    'version': '1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/chuc_vu.xml',
        'views/don_vi.xml',
        'views/phong_ban.xml',
        'views/nhan_vien.xml',
        'views/lich_su_cong_tac.xml',
        'views/chung_chi_bang_cap.xml',
        'views/danh_sach_chung_chi_bang_cap.xml',
        'views/hr_role.xml',
        'views/cham_cong.xml',
        'views/don_nghi_phep.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

