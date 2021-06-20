"""IG Account Activity Data Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations

from typing import List


class IGActivity:
    """Wrapper for IG Account Activity Data.
    
    Attributes:
        channel: The channel which triggered the activity e.g. WEB, MOBILE etc.
        date: The date of the activity item.
        deal_id: Unique identifier for deal.
        description: Activity description.
        details: Extra detail object for activity ('None' if no details).
        epic: Instrument epic identifier.
        period: The period of the activity item, e.g. "DFB" or "02-SEP-11".
        status: Action status e.g. ACCEPTED, REJECTED or UNKNOWN.
        type: Activity type e.g. POSITION, WORKING_ORDER etc.
    """

    def __init__(self,
                 channel: str,
                 date: str,
                 deal_id: str,
                 description: str,
                 details: str,
                 epic: str,
                 period: str,
                 status: str,
                 type: str):
        self.channel = channel
        self.date = date
        self.deal_id = deal_id
        self.description = description
        self.details = details
        self.epic = epic
        self.period = period
        self.status = status
        self.type = type

    @staticmethod
    def parse_from_dict(res: dict) -> List[IGActivity]:
        """ Parses IGActivity's from activity response dictionary.

        Args:
            res: Activity response dictionary.
        Returns:
            List of IGActivity's wrapping activity data.
        """
        activities = []
        for activity in res['activities']:
            activities.append(
                IGActivity(
                    activity['channel'],
                    activity['date'],
                    activity['dealId'],
                    activity['description'],
                    activity['details'],
                    activity['epic'],
                    activity['period'],
                    activity['status'],
                    activity['type']))
        return activities
