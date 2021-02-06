from icalendar import Calendar
from typing import Set, Union

from .text import TextUrlFinder
from urlfinderlib.url import URLList


class IcalUrlFinder:
    def __init__(self, blob: Union[bytes, str]):
        if isinstance(blob, str):
            blob = blob.encode('utf-8', errors='ignore')

        self.blob = blob

    def find_urls(self) -> Set[str]:
        urls = URLList()

        ical = Calendar.from_ical(self.blob)
        for component in ical.walk():
            if component.name == 'VEVENT':
                description = component.get('description')
                location = component.get('location')

                if description:
                    urls += TextUrlFinder(description).find_urls(strict=True)

                if location:
                    urls += TextUrlFinder(location).find_urls(strict=True)

        return set(urls)
