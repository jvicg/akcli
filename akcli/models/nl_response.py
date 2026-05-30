# /usr/bin/env python3

"""
Generated with `datamodel-code-generator` (https://github.com/koxudaxi/datamodel-code-generator)
and refined with manual adjustments.
"""

from __future__ import annotations

from typing import List, Optional

from ._base import BaseAPIModel


class Create(BaseAPIModel):
    href: Optional[str] = None
    method: Optional[str] = None


class Links(BaseAPIModel):
    create: Optional[Create] = None


class ActivateInProduction(BaseAPIModel):
    href: Optional[str] = None
    method: Optional[str] = None


class ActivateInStaging(BaseAPIModel):
    href: Optional[str] = None
    method: Optional[str] = None


class AppendItems(BaseAPIModel):
    href: Optional[str] = None
    method: Optional[str] = None


class Retrieve(BaseAPIModel):
    href: Optional[str] = None


class StatusInProduction(BaseAPIModel):
    href: Optional[str] = None


class StatusInStaging(BaseAPIModel):
    href: Optional[str] = None


class Update(BaseAPIModel):
    href: Optional[str] = None
    method: Optional[str] = None


class Links1(BaseAPIModel):
    activate_in_production: Optional[ActivateInProduction] = None
    activate_in_staging: Optional[ActivateInStaging] = None
    append_items: Optional[AppendItems] = None
    retrieve: Optional[Retrieve] = None
    status_in_production: Optional[StatusInProduction] = None
    status_in_staging: Optional[StatusInStaging] = None
    update: Optional[Update] = None


class NetworkList(BaseAPIModel):
    access_control_group: Optional[str] = None
    create_date: Optional[str] = None
    created_by: Optional[str] = None
    description: Optional[str] = None
    element_count: Optional[int] = None
    expedited_production_activation_status: Optional[str] = None
    expedited_staging_activation_status: Optional[str] = None
    is_upgrade_possible: Optional[bool] = None
    is_upgraded: Optional[bool] = None
    links: Optional[Links1] = None
    list: Optional[List[str]] = None
    name: Optional[str] = None
    network_list_type: Optional[str] = None
    production_activation_status: Optional[str] = None
    read_only: Optional[bool] = None
    shared: Optional[bool] = None
    staging_activation_status: Optional[str] = None
    sync_point: Optional[int] = None
    type: Optional[str] = None
    unique_id: Optional[str] = None
    update_date: Optional[str] = None
    updated_by: Optional[str] = None


class NLListResponse(BaseAPIModel):
    links: Optional[Links] = None
    network_lists: Optional[List[NetworkList]] = None
