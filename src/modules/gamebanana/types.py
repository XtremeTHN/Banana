from typing import TypedDict, Literal, Optional


SortType = Literal["new", "default", "updated"]
SubmissionType = Literal["Mod", "Tool", "Wip"]


class PagedRespondeMetadata(TypedDict):
    _nRecordCount: int
    _nPerpage: int
    _bIsComplete: bool


class PagedResponse(TypedDict):
    _aMetadata: PagedRespondeMetadata


class UpdateChanges(TypedDict):
    text: str
    cat: str


class Update(TypedDict):
    _sName: str
    _sText: str
    _aChangeLog: list[UpdateChanges]


class UpdatesResponse(PagedResponse):
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

    _sModelName: SubmissionType


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
    _sModelName: SubmissionType
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


class GenericProfile(TypedDict):
    _idRow: int
    _sName: str
    _sUserTitle: Optional[str]
    _sAvatarUrl: str


class SubmissionInfoCategory(TypedDict):
    _idRow: int
    _sName: str
    _sModelName: str
    _sIconUrl: str


class SubmissionInfoTrash(TypedDict):
    _aTrasher: GenericProfile
    _sReason: str


class SubmissionInfo(TypedDict):
    _idRow: int
    _sName: str
    _sText: str
    _sModelName: SubmissionType
    _aPreviewMedia: aIm
    _nDownloadCount: int
    _nViewCount: int
    _nLikeCount: int

    _bIsTrashed: bool
    _aTrashInfo: SubmissionInfoTrash

    _aCategory: SubmissionInfoCategory

    _sLicense: str
    _aLicenseChecklist: SubmissionInfoLicenseCheckList

    _aCredits: list[SubmissionInfoCreditsType]
    _aAlternateFileSources: list[SubmissionInfoAltFileSource]

    _aSubmitter: GenericProfile
    _aFiles: list[SubmissionInfoFileSource]


SubmissionWipCredits = TypedDict(
    "SubmissionWipCredits",
    {
        "Key Authors": list,
        "Original Authors": list,
        "Contributors": list,
        "Special Thanks": list,
    },
)


class SubmissionWip(SubmissionInfo):
    _sDevelopmentState: str
    _iCompletionPercentage: int
    _aCredits: SubmissionWipCredits
