# -*- coding: utf-8 -*-

from odoo import fields, models


class res_users(models.Model):
    """
    Override to let assign allowed locations on a user form
    """
    _inherit = "res.users"

    def _inverse_location_ids(self):
        """
        Inverse method for location_ids.
        The goal is to make sure location users are re-computed recursively

        Methods:
         * _compute_user_ids of stock.location
        """
        self = self.sudo()
        for user in self:
            for loc in user.location_ids:
                loc._compute_user_ids()

    location_ids = fields.Many2many(
        "stock.location",
        "res_users_stock_location_own_rel_table",
        "stock_location_own_id",
        "res_users_own_id",
        "Available Locations",
        inverse=_inverse_location_ids,
        help="The user will have access to this locations and all its child location",
    )
