from _typeshed import Incomplete
from xen.migration.verify import RecordError as RecordError
from xen.migration.verify import StreamError as StreamError
from xen.migration.verify import VerifyBase as VerifyBase


IHDR_FORMAT: str
IHDR_MARKER: int
IHDR_IDENT: int
IHDR_OPT_BIT_ENDIAN: int
IHDR_OPT_LE: Incomplete
IHDR_OPT_BE: Incomplete
IHDR_OPT_RESZ_MASK: int
DHDR_FORMAT: str
DHDR_TYPE_x86_pv: int
DHDR_TYPE_x86_hvm: int
dhdr_type_to_str: Incomplete
RH_FORMAT: str
REC_TYPE_end: int
REC_TYPE_page_data: int
REC_TYPE_x86_pv_info: int
REC_TYPE_x86_pv_p2m_frames: int
REC_TYPE_x86_pv_vcpu_basic: int
REC_TYPE_x86_pv_vcpu_extended: int
REC_TYPE_x86_pv_vcpu_xsave: int
REC_TYPE_shared_info: int
REC_TYPE_tsc_info: int
REC_TYPE_hvm_context: int
REC_TYPE_hvm_params: int
REC_TYPE_toolstack: int
REC_TYPE_x86_pv_vcpu_msrs: int
REC_TYPE_verify: int
REC_TYPE_checkpoint: int
REC_TYPE_checkpoint_dirty_pfn_list: int
REC_TYPE_static_data_end: int
REC_TYPE_x86_cpuid_policy: int
REC_TYPE_x86_msr_policy: int
rec_type_to_str: Incomplete
PAGE_DATA_FORMAT: str
PAGE_DATA_PFN_MASK: Incomplete
PAGE_DATA_PFN_RESZ_MASK: Incomplete
PAGE_DATA_TYPE_SHIFT: int
PAGE_DATA_TYPE_LTABTYPE_MASK: Incomplete
PAGE_DATA_TYPE_LTAB_MASK: Incomplete
PAGE_DATA_TYPE_LPINTAB: Incomplete
PAGE_DATA_TYPE_NOTAB: Incomplete
PAGE_DATA_TYPE_L1TAB: Incomplete
PAGE_DATA_TYPE_L2TAB: Incomplete
PAGE_DATA_TYPE_L3TAB: Incomplete
PAGE_DATA_TYPE_L4TAB: Incomplete
PAGE_DATA_TYPE_BROKEN: Incomplete
PAGE_DATA_TYPE_XALLOC: Incomplete
PAGE_DATA_TYPE_XTAB: Incomplete
X86_PV_INFO_FORMAT: str
X86_PV_P2M_FRAMES_FORMAT: str
X86_PV_VCPU_HDR_FORMAT: str
X86_TSC_INFO_FORMAT: str
HVM_PARAMS_ENTRY_FORMAT: str
HVM_PARAMS_FORMAT: str
X86_CPUID_POLICY_FORMAT: str
X86_MSR_POLICY_FORMAT: str

class VerifyLibxc(VerifyBase):
    version: int
    squashed_pagedata_records: int
    def __init__(self, info, read) -> None: ...
    def verify(self) -> None: ...
    def verify_ihdr(self) -> None: ...
    def verify_dhdr(self) -> None: ...
    def verify_record(self): ...
    def verify_record_end(self, content) -> None: ...
    def verify_record_page_data(self, content) -> None: ...
    def verify_record_x86_pv_info(self, content) -> None: ...
    def verify_record_x86_pv_p2m_frames(self, content) -> None: ...
    def verify_record_x86_pv_vcpu_generic(self, content, name) -> None: ...
    def verify_record_shared_info(self, content) -> None: ...
    def verify_record_tsc_info(self, content) -> None: ...
    def verify_record_hvm_context(self, content) -> None: ...
    def verify_record_hvm_params(self, content) -> None: ...
    def verify_record_toolstack(self, _) -> None: ...
    def verify_record_verify(self, content) -> None: ...
    def verify_record_checkpoint(self, content) -> None: ...
    def verify_record_checkpoint_dirty_pfn_list(self, content) -> None: ...
    def verify_record_static_data_end(self, content) -> None: ...
    def verify_record_x86_cpuid_policy(self, content) -> None: ...
    def verify_record_x86_msr_policy(self, content) -> None: ...

record_verifiers: Incomplete
