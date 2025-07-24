import requests
from ..utils import Thread
from typing import Callable

from .types import Submission, SubmissionInfo, SortType, QuerySubmission

FNF_GAME_ID = "8694"
GB_API = "https://gamebanana.com/apiv11"


def get(url, cb, *args):
    Thread(lambda: cb(requests.get(url).json(), *args)).start()


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
            f"{GB_API}/Game/{FNF_GAME_ID}/Subfeed?_nPage={page}&_sSort={sort}&_sName={query}",
            cb,
            page,
        )

    @staticmethod
    def get_submission_info(
        submission_type: str, submission_id: str, cb: Callable[[SubmissionInfo], None]
    ):
        get(f"{GB_API}/{submission_type}/{submission_id}/ProfilePage", cb)

    @staticmethod
    def get_top_submissions(callback: Callable[[list[Submission]], None]):
        get(f"{GB_API}/Game/{FNF_GAME_ID}/TopSubs", callback)

    @staticmethod
    def get_featured_submissions(cb: Callable[[list[SubmissionInfo]], None], pages=1):
        get(
            f"{GB_API}/Util/List/Featured?_nPage={pages}&_idGameRow={FNF_GAME_ID}",
            lambda x: cb(x["_aRecords"]),
        )
