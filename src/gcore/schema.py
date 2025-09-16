import enum
import json
import typing

import pydantic

from .anyuri import AnyUri


class Language(str, enum.Enum):
    """
    如何產生這裡的語言清單:
    1. 查詢BERT支援的語言列表 https://github.com/google-research/bert/blob/master/multilingual.md#list-of-languages
    2. 優先使用 http://www.lingoes.net/en/translator/langcode.htm 裡的 language code
    3. 如果上面找不到，就到 https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes 找 language code
    4. 因為冰島語(is)、印尼語(is)是 Python 保留字，暫時先拿掉
    5. 粵語(廣東話) 收錄在 ISO 639-3
    """

    af = "af"  # Afrikaans
    sq = "sq"  # Albanian
    ar = "ar"  # Arabic
    hy = "hy"  # Armenian
    az = "az"  # Azerbaijani
    eu = "eu"  # Basque
    be = "be"  # Belarusian
    bs_ba = "bs-ba"  # Bosnian
    bg = "bg"  # Bulgarian
    ca = "ca"  # Catalan
    zh_cn = "zh-cn"  # Chinese (Simplified)
    zh_tw = "zh-tw"  # Chinese (Traditional)
    hr = "hr"  # Croatian
    cs = "cs"  # Czech
    da = "da"  # Danish
    nl = "nl"  # Dutch
    en = "en"  # English
    et = "et"  # Estonian
    fi = "fi"  # Finnish
    fr = "fr"  # French
    gl = "gl"  # Galician
    ka = "ka"  # Georgian
    de = "de"  # German
    el = "el"  # Greek
    gu = "gu"  # Gujarati
    he = "he"  # Hebrew
    hi = "hi"  # Hindi
    hu = "hu"  # Hungarian
    is_ = "is"  # Icelandic
    id_ = "id"  # Indonesian
    it = "it"  # Italian
    ja = "ja"  # Japanese
    kn = "kn"  # Kannada
    kk = "kk"  # Kazakh
    ko = "ko"  # Korean
    lv = "lv"  # Latvian
    lt = "lt"  # Lithuanian
    mk = "mk"  # Macedonian
    mn = "mn"  # Mongolian
    ms = "ms"  # Malay
    mr = "mr"  # Marathi
    nb = "nb"  # Norwegian (Bokmal)
    nn_no = "nn-no"  # Norwegian (Nynorsk)
    pl = "pl"  # Polish
    pt = "pt"  # Portuguese
    pa = "pa"  # Punjabi
    ro = "ro"  # Romanian
    ru = "ru"  # Russian
    sk = "sk"  # Slovak
    sl = "sl"  # Slovenian
    es = "es"  # Spanish
    sw = "sw"  # Swahili
    sv = "sv"  # Swedish
    tl = "tl"  # Tagalog
    ta = "ta"  # Tamil
    th = "th"  # Thai
    tt = "tt"  # Tatar
    te = "te"  # Telugu
    tr = "tr"  # Turkish
    uk = "uk"  # Ukrainian
    ur = "ur"  # Urdu
    uz = "uz"  # Uzbek
    vi = "vi"  # Vietnamese
    cy = "cy"  # Welsh
    yue = "yue"  # Yue Chinese (Cantonese)


FULL_LANG = {
    Language.af: "Afrikaans",
    Language.sq: "Albanian",
    Language.ar: "Arabic",
    Language.hy: "Armenian",
    Language.az: "Azerbaijani",
    Language.eu: "Basque",
    Language.be: "Belarusian",
    Language.bs_ba: "Bosnian",
    Language.bg: "Bulgarian",
    Language.ca: "Catalan",
    Language.zh_cn: "Chinese (Simplified)",
    Language.zh_tw: "Chinese (Traditional)",
    Language.hr: "Croatian",
    Language.cs: "Czech",
    Language.da: "Danish",
    Language.nl: "Dutch",
    Language.en: "English",
    Language.et: "Estonian",
    Language.fi: "Finnish",
    Language.fr: "French",
    Language.gl: "Galician",
    Language.ka: "Georgian",
    Language.de: "German",
    Language.el: "Greek",
    Language.gu: "Gujarati",
    Language.he: "Hebrew",
    Language.hi: "Hindi",
    Language.hu: "Hungarian",
    Language.is_: "Icelandic",
    Language.id_: "Indonesian",
    Language.it: "Italian",
    Language.ja: "Japanese",
    Language.kn: "Kannada",
    Language.kk: "Kazakh",
    Language.ko: "Korean",
    Language.lv: "Latvian",
    Language.lt: "Lithuanian",
    Language.mk: "Macedonian",
    Language.mn: "Mongolian",
    Language.ms: "Malay",
    Language.mr: "Marathi",
    Language.nb: "Norwegian (Bokmal)",
    Language.nn_no: "Norwegian (Nynorsk)",
    Language.pl: "Polish",
    Language.pt: "Portuguese",
    Language.pa: "Punjabi",
    Language.ro: "Romanian",
    Language.ru: "Russian",
    Language.sk: "Slovak",
    Language.sl: "Slovenian",
    Language.es: "Spanish",
    Language.sw: "Swahili",
    Language.sv: "Swedish",
    Language.tl: "Tagalog",
    Language.ta: "Tamil",
    Language.th: "Thai",
    Language.tt: "Tatar",
    Language.te: "Telugu",
    Language.tr: "Turkish",
    Language.uk: "Ukrainian",
    Language.ur: "Urdu",
    Language.uz: "Uzbek",
    Language.vi: "Vietnamese",
    Language.cy: "Welsh",
    Language.yue: "Yue Chinese (Cantonese)",
}


class MediaType(str, enum.Enum):
    image = "image"
    audio = "audio"
    video = "video"


class Region(str, enum.Enum):
    # https://zh.wikipedia.org/wiki/ISO_3166-2

    dz = "dz"  # Algeria
    cn = "cn"  # China
    fr = "fr"  # France
    gr = "gr"  # Greece
    hk = "hk"  # Hong Kong
    in_ = "in"  # India
    id = "id"  # Indonesia
    it = "it"  # Italy
    jp = "jp"  # Japan
    ke = "ke"  # Kenya
    kr = "kr"  # Korea (the Republic of)
    my = "my"  # Malaysia
    mx = "mx"  # Mexico
    nz = "nz"  # New Zealand
    ng = "ng"  # Nigeria
    ph = "ph"  # Philippines
    ru = "ru"  # Russian
    sa = "sa"  # Saudi Arabia
    sg = "sg"  # Singapore
    es = "es"  # Spain
    tw = "tw"  # Taiwan
    th = "th"  # Thailand
    tr = "tr"  # Turkey
    us = "us"  # United States
    vn = "vn"  # Viet Nam

    world = "world"  # world
    other = "other"  # other


class BaseModel(pydantic.BaseModel):
    def to_primitive(self) -> typing.Any:
        return json.loads(self.json())


class MediaBaseModel(BaseModel):
    type: MediaType

    uri: typing.Optional[AnyUri] = None  # the identifier

    title: typing.Optional[str] = None
    description: typing.Optional[str] = None

    width: typing.Optional[int] = None
    height: typing.Optional[int] = None
    duration: typing.Optional[float] = None

    preview: typing.Optional[AnyUri] = None  # the preview link
    thumbnail: typing.Optional[AnyUri] = None  # the thumbnail link
    download: typing.Optional[AnyUri] = None  # the download link

    class Config:
        anystr_strip_whitespace = True
