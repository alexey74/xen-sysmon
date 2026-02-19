from struct import unpack_from as unpack_from

from _typeshed import Incomplete
from xen.migration.libxc import VerifyLibxc as VerifyLibxc
from xen.migration.verify import RecordError as RecordError
from xen.migration.verify import StreamError as StreamError
from xen.migration.verify import VerifyBase as VerifyBase


HDR_FORMAT: str
HDR_IDENT: int
HDR_VERSION: int
HDR_OPT_BIT_ENDIAN: int
HDR_OPT_BIT_LEGACY: int
HDR_OPT_LE: Incomplete
HDR_OPT_BE: Incomplete
HDR_OPT_LEGACY: Incomplete
HDR_OPT_RESZ_MASK: int
RH_FORMAT: str
REC_TYPE_end: int
REC_TYPE_libxc_context: int
REC_TYPE_emulator_xenstore_data: int
REC_TYPE_emulator_context: int
REC_TYPE_checkpoint_end: int
REC_TYPE_checkpoint_state: int
rec_type_to_str: Incomplete
EMULATOR_HEADER_FORMAT: str
EMULATOR_ID_unknown: int
EMULATOR_ID_qemu_trad: int
EMULATOR_ID_qemu_upstream: int
emulator_id_to_str: Incomplete
LIBXL_QEMU_SIGNATURE: str
LIBXL_QEMU_RECORD_HDR: Incomplete

class VerifyLibxl(VerifyBase):
    def __init__(self, info, read) -> None: ...
    def verify(self) -> None: ...
    def verify_hdr(self) -> None: ...
    def verify_record(self): ...
    def verify_record_end(self, content) -> None: ...
    def verify_record_libxc_context(self, content) -> None: ...
    def verify_record_emulator_xenstore_data(self, content) -> None: ...
    def verify_record_emulator_context(self, content) -> None: ...
    def verify_record_checkpoint_end(self, content) -> None: ...
    def verify_record_checkpoint_state(self, content) -> None: ...

record_verifiers: Incomplete
