import requests
from ..utils import Thread
from typing import Callable

from .types import Submission, SubmissionInfo, SortType, PagedRespondeMetadata

GAME_ID = "8694"
GB_API = "https://gamebanana.com/apiv11"


def get_sync(url):
    return requests.get(url).json()


def get(url, cb, *args):
    Thread(lambda: cb(get_sync(url), *args)).start()


class PagedResponse:
    def __init__(self, url):
        self.url: str = url
        self.index = 1
        self.finished = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.finished:
            raise StopIteration

        cnt = get_sync(self.url.replace("%PAGE%", str(self.index)))

        if cnt["_aMetadata"]["_bIsComplete"] is True:
            self.finished = True

        self.index += 1
        return cnt["_aRecords"]


class Gamebanana:
    @staticmethod
    def query_submissions(
        query: str,
        cb: Callable[[dict, int], None],
        sort: SortType = "new",
        page=1,
    ):
        """
        It wil return a dictionary with a key (_aRecords) holding all the results.
        """
        get(
            f"{GB_API}/Game/{GAME_ID}/Subfeed?_nPage={page}&_sSort={sort}&_sName={query}",
            cb,
            page,
        )

    @staticmethod
    def get_submission_info(
        submission_type: str, submission_id: str, cb: Callable[[SubmissionInfo], None]
    ):
        get(f"{GB_API}/{submission_type}/{submission_id}/ProfilePage", cb)

    @staticmethod
    def get_submission_updates(
        submission_type: str,
        submission_id: str,
    ):
        """Warning: synchronous method"""
        return PagedResponse(
            f"{GB_API}/{submission_type}/{submission_id}/Updates?_nPage=%PAGE%&_nPerpage=10"
        )

    @staticmethod
    def get_top_submissions(callback: Callable[[list[Submission]], None]):
        get(f"{GB_API}/Game/{GAME_ID}/TopSubs", callback)

    @staticmethod
    def get_featured_submissions(cb: Callable[[list[SubmissionInfo]], None], pages=1):
        get(
            f"{GB_API}/Util/List/Featured?_nPage={pages}&_idGameRow={GAME_ID}",
            lambda x: cb(x["_aRecords"]),
        )
