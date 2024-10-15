from typing import Dict, List

# Common groups of recipients
ALL_RECIPIENTS = ["Pilot", "Unmooring", "Tugboat", "ShippingAgent", "ShippingCompany", "LoadingUnloading"]
STANDARD_RECIPIENTS = ["Unmooring", "Tugboat", "ShippingAgent", "ShippingCompany", "CIQS"]
STANDARD_RECIPIENTS_WITH_LOADING = STANDARD_RECIPIENTS + ["LoadingUnloading"]
PILOT_UNMOORING_TUGBOAT = ["Pilot", "Unmooring", "Tugboat"]
PILOT_UNMOORING_TUGBOAT_LOADING = PILOT_UNMOORING_TUGBOAT + ["LoadingUnloading"]

INOUT_PILOTAGE_EVENTS = ["新增引水申請", "更新引水時間", "引水人上船時間"]
BERTH_ORDER_EVENTS = ["通過10浬時間", "通過5浬時間"]

notification_mapping: Dict[str, List[str]] = {
    "進港預報申請": PILOT_UNMOORING_TUGBOAT_LOADING,
    "修改進港預報": PILOT_UNMOORING_TUGBOAT_LOADING,
    "新增引水申請 (進港)": PILOT_UNMOORING_TUGBOAT_LOADING,
    "更新引水時間 (進港)": PILOT_UNMOORING_TUGBOAT_LOADING,
    "船長報告ETA": ALL_RECIPIENTS,
    "引水人上船時間 (進港)": STANDARD_RECIPIENTS_WITH_LOADING,
    "實際靠妥時間": ["ShippingAgent", "ShippingCompany", "LoadingUnloading", "CIQS"],
    "出港預報申請": PILOT_UNMOORING_TUGBOAT,
    "修改出港預報": PILOT_UNMOORING_TUGBOAT,
    "新增引水申請 (出港)": PILOT_UNMOORING_TUGBOAT_LOADING,
    "更新引水時間 (出港)": PILOT_UNMOORING_TUGBOAT_LOADING,
    "引水人上船時間 (出港)": STANDARD_RECIPIENTS,
    "離開泊地時間": ["ShippingAgent", "ShippingCompany"],
    "通過15浬時間": ["ShippingAgent", "ShippingCompany"],
    "通過10浬時間": ALL_RECIPIENTS,
    "通過5浬時間": ALL_RECIPIENTS
}