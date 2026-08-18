from odoo import api, fields, models


class RsProjects(models.Model):
    _inherit = 'rs.project'

    gross_area = fields.Float(
        string='Gross Area',
        required=False)
    check_number = fields.Char(
        string='Check number',
        required=False)
    check_type = fields.Char(
        string='Check Type',
        required=False)
    issuer = fields.Char(
        string='Issuer', 
        required=False)
    issue_place = fields.Char(
        string='Place of Issue ', 
        required=False)
    title_deed_no = fields.Char(
        string='Title Deed No',
        required=False)
    parking_lots_number = fields.Integer(
        string='Parking Lots Number',
        required=False)
    elevators_number = fields.Integer(
        string='Elevators Number',
        required=False)
