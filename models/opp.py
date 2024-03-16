from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def send_notification_to_ntfy(self, message, title="Notification", priority="high", tags=None):
        """
        Sends a notification message to an NTFY server.

        Args:
            message (str): The message to be sent in the notification.
            title (str): The title of the notification. Default is "Notification".
            priority (str): The priority of the notification. Default is "normal".
            tags (list or None): Optional tags for the notification.
        """
        url = "https://push.simstech.cloud/simstech-odoo-alerts"
        # Encode your message in UTF-8
        data = message.encode('utf-8')
        headers = {
            "Title": title,
            "Priority": priority
        }
        if tags:
            if isinstance(tags, str):
                tags = [tags]
            headers["Tags"] = ','.join(tags)

        try:
            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 200:
                _logger.info("Notification sent successfully")
            else:
                # Log more error details
                _logger.error("Failed to send notification. Status code: %s, Response: %s", response.status_code, response.text)
        except Exception as e:
            _logger.error("Failed to send notification. Exception: %s", str(e))


    def create(self, vals):
        """
        Overrides the create method to send a notification when a new CRM record is created.

        Args:
            vals (dict): The dictionary of values for the record being created.

        Returns:
            object: The created record.
        """
        record = super(CrmLead, self).create(vals)
        message = f"A new CRM record has been created: {record.name}"
        self.send_notification_to_ntfy(message, title="New CRM Record Created")
        return record

    # @api.onchange('stage_id')
    # def onchange_stage_id(self):
    #     """
    #     Sends a notification to NTFY when the stage of the opportunity is changed.

    #     Args:
    #         self (object): The CRM lead object.
    #     """
    #     _logger.info("Stage changed to %s", self.stage_id.name)
    #     message = f"The stage of the opportunity has been changed to {self.stage_id.name}"
    #     self.send_notification_to_ntfy(message, title="Opportunity Stage Changed")
