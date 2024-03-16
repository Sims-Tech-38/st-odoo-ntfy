from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def send_notification_to_ntfy(self, message, title="Notification", priority="high", tags=None):
        """
        Sends a notification message to an NTFY server, including a link to the CRM lead record.

        Args:
            message (str): The message to be sent in the notification.
            title (str): The title of the notification. Default is "Notification".
            priority (str): The priority of the notification. Default is "normal".
            tags (list or None): Optional tags for the notification.
        """
        # Construct the link to the CRM record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        record_url = f"{base_url}/web#id={self.id}&model=crm.lead&view_type=form"
        full_message = f"{message}\n\nView Record: {record_url}"

        # Prepare the notification payload
        data = full_message.encode('utf-8')
        headers = {
            "Title": title,
            "Priority": priority
        }
        if tags:
            if isinstance(tags, str):
                tags = [tags]
            headers["Tags"] = ','.join(tags)

        # Send the notification
        url = "https://push.simstech.cloud/simstech-odoo-alerts"
        try:
            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 200:
                _logger.info("Notification sent successfully")
            else:
                _logger.error("Failed to send notification. Status code: %s", response.status_code)
        except Exception as e:
            _logger.error("Failed to send notification. Exception: %s", str(e))

    def create(self, vals):
        """
        Overrides the create method to send a notification when a new CRM record is created.
        """
        record = super(CrmLead, self).create(vals)
        message = f"A new CRM record has been created: {record.name}"
        self.send_notification_to_ntfy(message, title="New CRM Record Created")
        return record

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        """
        Sends a notification to NTFY when the stage of the opportunity is changed.
        """
        _logger.info("Stage changed to %s", self.stage_id.name)
        message = f"The stage of the opportunity has been changed to {self.stage_id.name}"
        self.send_notification_to_ntfy(message, title="Opportunity Stage Changed")
