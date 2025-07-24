from typing import TypedDict, Literal


SortType = Literal["new", "default", "updated"]


class PagedRespondeMetadata(TypedDict):
    _nRecordCount: int
    _nPerpage: int
    _bIsComplete: bool


class UpdateChanges(TypedDict):
    text: str
    cat: str


class Update(TypedDict):
    _sName: str
    _sText: str
    _aChangeLog: list[UpdateChanges]


class UpdatesResponse(TypedDict):
    _aMetadata: PagedRespondeMetadata
    _aRecords: list[Update]


class Submitter(TypedDict):
    _sName: str
    _sAvatarUrl: str


class Submission(TypedDict):
    _idRow: int
    _sName: str
    _sDescription: str
    _sImageUrl: str
    _sThumbnailUrl: str
    _sPeriod: str
    _aSubmitter: Submitter

    _sModelName: str


class PreviewImage(TypedDict):
    _sType: str
    _sBaseUrl: str
    _sFile: str


class aIm(TypedDict):
    _aImages: list[PreviewImage]


class SubmissionStudio(TypedDict):
    _sName: str


class QuerySubmission(TypedDict):
    _idRow: int
    _sModelName: str
    _sName: str
    _aPreviewMedia: aIm

    _aSubmitter: Submitter
    _aStudio: SubmissionStudio

    _nViewCount: int
    _nLikeCount: int


class SubmissionInfoLicenseCheckList(TypedDict):
    yes: list[str]
    ask: list[str]
    no: list[str]


class SubmissionInfoCredits(TypedDict):
    _sRole: str
    _sName: str
    # TODO: maybe add the author pfp


class SubmissionInfoCreditsType(TypedDict):
    _sGroupName: str
    _aAuthors: list[SubmissionInfoCredits]
    # key_authors: list[list[str]]


class SubmissionInfoFileSource(TypedDict):
    _idRow: int
    _sFile: str
    _nFilesize: str
    _sDownloadUrl: str
    _sMd5Checksum: str
    _sDescription: str
    _bHasContents: bool


class SubmissionInfoAltFileSource(TypedDict):
    url: str
    description: str


class SubmissionInfoSubmitter(TypedDict):
    _idRow: int
    _sName: str
    _sUserTitle: str
    _sAvatarUrl: str


class SubmissionInfo(TypedDict):
    _idRow: int
    _sName: str
    _sText: str
    _aPreviewMedia: aIm
    _nDownloadCount: int
    _nViewCount: int
    _nLikeCount: int

    _sLicense: str
    _aLicenseChecklist: SubmissionInfoLicenseCheckList

    _aCredits: list[SubmissionInfoCreditsType]
    _aAlternateFileSources: list[SubmissionInfoAltFileSource]

    _aSubmitter: SubmissionInfoSubmitter
    _aFiles: list[SubmissionInfoFileSource]
