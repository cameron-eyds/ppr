# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=too-few-public-methods

"""This module holds methods to support registration model mapping to dict/json."""
from mhr_api.models import utils as model_utils
from mhr_api.models.registration_utils import find_cancelled_note, get_document_description, include_caution_note
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrLocationTypes,
    MhrNoteStatusTypes,
    MhrOwnerStatusTypes,
    MhrPartyTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
    MhrStatusTypes,
)
from mhr_api.utils.logging import logger

from .mhr_note import MhrNote


def set_payment_json(registration, reg_json: dict) -> dict:
    """Add registration payment info json if payment exists."""
    if registration.pay_invoice_id and registration.pay_path:
        payment = {"invoiceId": str(registration.pay_invoice_id), "receipt": registration.pay_path}
        reg_json["payment"] = payment
    return reg_json


def set_current_misc_json(registration, reg_json: dict, search: bool = False) -> dict:
    """Add miscellaneous current view registration properties."""
    dec_value: int = 0
    dec_ts = None
    own_land: bool = False
    if registration.documents[0].own_land and registration.documents[0].own_land == "Y":
        own_land = True
    if registration.change_registrations:
        for reg in registration.change_registrations:
            doc = reg.documents[0]
            if reg.is_transfer() or reg.documents[0].document_type in (
                MhrDocumentTypes.REG_103,
                MhrDocumentTypes.REG_103E,
                MhrDocumentTypes.AMEND_PERMIT,
                MhrDocumentTypes.STAT,
                MhrDocumentTypes.REGC_CLIENT,
                MhrDocumentTypes.REGC_STAFF,
                MhrDocumentTypes.REGC,
                MhrDocumentTypes.PUBA,
            ):
                own_land = bool(doc.own_land and doc.own_land == "Y")
                # logger.debug(f'doc type={doc.document_type} own land={doc.own_land}')
            if (
                reg.is_transfer()
                and doc.declared_value
                and doc.declared_value > 0
                and (dec_ts is None or reg.registration_ts > dec_ts)
            ):
                dec_value = doc.declared_value
                dec_ts = reg.registration_ts
    reg_json["declaredValue"] = dec_value
    if dec_ts:
        reg_json["declaredDateTime"] = model_utils.format_ts(dec_ts)
    reg_json["ownLand"] = own_land
    if not search:
        reg_json = set_permit_json(registration, reg_json)
        reg_json = set_exempt_json(registration, reg_json)
    return reg_json


def set_permit_json(registration, reg_json: dict) -> dict:  # pylint: disable=too-many-branches; just one more.
    """Conditinally add the latest transport permit information if available."""
    if not registration or not reg_json or not registration.change_registrations:
        return reg_json
    permit_number: str = None
    permit_ts = None
    expiry_ts = None
    permit_status = None
    permit_reg_id: int = 0
    permit_doc_type: str = None
    for reg in registration.change_registrations:
        if reg.documents[0].document_type == MhrDocumentTypes.REG_103:
            permit_number = reg.documents[0].document_registration_number
            permit_ts = reg.registration_ts
            # logger.debug(f'set_permit # {permit_number}')
        # Registrations are in chronological order: get the latest permit, use latest amendment status, expiry.
        if reg.documents[0].document_type in (
            MhrDocumentTypes.REG_103,
            MhrDocumentTypes.REG_103E,
            MhrDocumentTypes.AMEND_PERMIT,
        ):
            if reg.notes:
                permit_status = reg.notes[0].status_type
                expiry_ts = reg.notes[0].expiry_date
                permit_doc_type = reg.documents[0].document_type
                # logger.debug(f'set permit reg id {reg.id} set_permit status {permit_status}')
            permit_reg_id = reg.id
    if permit_number:
        reg_json["permitRegistrationNumber"] = permit_number
        reg_json["permitDateTime"] = model_utils.format_ts(permit_ts)
        if permit_status:
            reg_json["permitStatus"] = permit_status
        if expiry_ts:
            if (
                permit_status
                and permit_status == MhrNoteStatusTypes.ACTIVE
                and expiry_ts.timestamp() < model_utils.now_ts().timestamp()
            ):
                reg_json["permitStatus"] = MhrNoteStatusTypes.EXPIRED
            reg_json["permitExpiryDateTime"] = model_utils.format_ts(expiry_ts)
        if reg_json.get("location") and permit_status == MhrNoteStatusTypes.ACTIVE:
            reg_json["location"]["permitWithinSamePark"] = is_same_mh_park(registration, reg_json)
        if permit_reg_id:
            for reg in registration.change_registrations:
                if reg.id == permit_reg_id and reg.draft:
                    reg_json["permitLandStatusConfirmation"] = reg.draft.draft.get("landStatusConfirmation", False)
        if "permitLandStatusConfirmation" not in reg_json:
            reg_json["permitLandStatusConfirmation"] = False
        reg_json["permitExtended"] = permit_doc_type and permit_doc_type == MhrDocumentTypes.REG_103E
        if permit_status and permit_status == MhrNoteStatusTypes.ACTIVE:
            reg_json["previousLocation"] = get_permit_previous_location_json(registration)
    return reg_json


def get_permit_previous_location_json(registration) -> dict:
    """When an active transport permit exists, get the previous location for restoring with a cancel permit."""
    loc_json = {}
    if not registration or not registration.change_registrations:
        return loc_json
    permit_reg_id: int = 0
    for reg in registration.change_registrations:
        if reg.documents[0].document_type == MhrDocumentTypes.REG_103:
            permit_reg_id = reg.id
    if permit_reg_id:
        if (
            registration.locations
            and registration.locations[0].registration_id < permit_reg_id
            and registration.locations[0].change_registration_id == permit_reg_id
        ):
            loc_json = registration.locations[0].json
        else:
            for reg in registration.change_registrations:
                if (
                    reg.locations
                    and reg.locations[0].registration_id < permit_reg_id
                    and reg.locations[0].change_registration_id == permit_reg_id
                ):
                    loc_json = reg.locations[0].json
                    break
    return loc_json


def is_same_mh_park(registration, reg_json: dict) -> bool:
    """When an active transport permits exists indicate if the location change was within the same MH park."""
    if not registration or not reg_json or not registration.change_registrations or not reg_json.get("location"):
        return False
    if not reg_json["location"].get("locationType") == MhrLocationTypes.MH_PARK:
        return False
    loc_reg_id: int = 0
    for reg in registration.change_registrations:
        if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
            loc_reg_id = reg.id
            break
    for reg in registration.change_registrations:
        if (
            reg.locations
            and reg.locations[0].status_type != MhrStatusTypes.ACTIVE
            and reg.locations[0].change_registration_id == loc_reg_id
            and reg.locations[0].location_type == MhrLocationTypes.MH_PARK
        ):
            current_name: str = str(reg_json["location"].get("parkName")).upper()
            return current_name == reg.locations[0].park_name
    return False


def set_exempt_json(registration, reg_json: dict) -> dict:
    """Conditionally add exemptDateTime as the timestamp of the registration that set the exempt status."""
    if not registration or not reg_json or not reg_json.get("status") == MhrRegistrationStatusTypes.EXEMPT:
        return reg_json
    exempt_ts = None
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if (
                reg.documents[0].document_type in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR)
                and reg.notes
                and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
            ):
                exempt_ts = reg.registration_ts
                break
        if (
            not exempt_ts
            and reg_json.get("location")
            and reg_json["location"]["address"].get("region")
            and reg_json["location"]["address"].get("region") != "BC"
        ):  # must be either location outside of BC.
            for reg in registration.change_registrations:
                if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
                    exempt_ts = reg.registration_ts
                    break
    # Or conversion / initial registration set status to exempt
    if not exempt_ts and registration.registration_type in (
        MhrRegistrationTypes.MHREG,
        MhrRegistrationTypes.MHREG_CONVERSION,
    ):
        exempt_ts = registration.registration_ts
    if exempt_ts:
        reg_json["exemptDateTime"] = model_utils.format_ts(exempt_ts)
    return reg_json


def set_submitting_json(registration, reg_json: dict) -> dict:
    """Build the submitting party JSON if available."""
    if reg_json and registration.parties:
        for party in registration.parties:
            if party.party_type == MhrPartyTypes.SUBMITTING:
                reg_json["submittingParty"] = party.json
                break
    return reg_json


def set_location_json(registration, reg_json: dict, current: bool) -> dict:
    """Add location properties to the registration JSON based on current."""
    if not current and registration.registration_type not in (
        MhrRegistrationTypes.MHREG,
        MhrRegistrationTypes.MHREG_CONVERSION,
        MhrRegistrationTypes.PERMIT,
        MhrRegistrationTypes.PERMIT_EXTENSION,
        MhrRegistrationTypes.AMENDMENT,
        MhrRegistrationTypes.REG_STAFF_ADMIN,
    ):
        return reg_json
    location = None
    if registration.locations:
        loc = registration.locations[0]
        if (current or registration.current_view) and loc.status_type == MhrStatusTypes.ACTIVE:
            location = loc
        elif not (current or registration.current_view) and loc.registration_id == registration.id:
            location = loc
    if not location and current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations:
                loc = reg.locations[0]
                if loc.status_type == MhrStatusTypes.ACTIVE:
                    location = loc
    if location:
        if (
            reg_json.get("registrationType", "")
            in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.PERMIT_EXTENSION, MhrRegistrationTypes.AMENDMENT)
            and not current
        ):
            reg_json["newLocation"] = location.json
        else:
            reg_json["location"] = location.json
    return reg_json


def get_sections_json(registration, reg_id) -> dict:
    """Build the description sections JSON from the registration id."""
    sections = []
    desc_reg = None
    if registration.id == reg_id:
        desc_reg = registration
    elif registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.id == reg_id:
                desc_reg = reg
                break
    if desc_reg and desc_reg.sections:
        for section in desc_reg.sections:
            sections.append(section.json)
    return sections


def set_description_json(registration, reg_json, current: bool, doc_type: str = None) -> dict:
    """Build the description JSON conditional on current."""
    if not current and registration.registration_type not in (
        MhrRegistrationTypes.MHREG,
        MhrRegistrationTypes.MHREG_CONVERSION,
        MhrRegistrationTypes.REG_STAFF_ADMIN,
    ):
        return reg_json
    if (
        not current
        and registration.registration_type == MhrRegistrationTypes.REG_STAFF_ADMIN
        and doc_type
        and doc_type
        not in (
            MhrDocumentTypes.PUBA,
            MhrDocumentTypes.REGC,
            MhrDocumentTypes.REGC_CLIENT,
            MhrDocumentTypes.REGC_STAFF,
            MhrDocumentTypes.EXRE,
        )
    ):
        return reg_json
    description = None
    if registration.descriptions:
        desc = registration.descriptions[0]
        if (current or registration.current_view) and desc.status_type == MhrStatusTypes.ACTIVE:
            description = desc
        elif not (current or registration.current_view) and desc.registration_id == registration.id:
            description = desc
    if not description and current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.descriptions:
                desc = reg.descriptions[0]
                if desc.status_type == MhrStatusTypes.ACTIVE:
                    description = desc
    if description:
        description_json = description.json
        description_json["sections"] = get_sections_json(registration, description.registration_id)
        reg_json["description"] = description_json
    return reg_json


def sort_owner_groups(owner_groups: dict, cleanup: bool = False) -> dict:
    """Sort tenants in common owner groups by group sequence number, remove groupSequenceNumber."""
    if not owner_groups:
        return owner_groups
    if len(owner_groups) == 1:
        if cleanup and owner_groups[0].get("groupSequenceNumber"):
            del owner_groups[0]["groupSequenceNumber"]
        return owner_groups
    sorted_groups = sort_common_owner_groups(owner_groups)
    if cleanup:
        for group in sorted_groups:
            if group.get("groupSequenceNumber"):
                del group["groupSequenceNumber"]
    return sorted_groups


def cleanup_owner_groups(reg_json: dict) -> dict:
    """Cleanup registration owner groups, removing groupSequenceNumber."""
    if reg_json.get("ownerGroups"):
        for group in reg_json.get("ownerGroups"):
            if group.get("groupSequenceNumber"):
                del group["groupSequenceNumber"]
    if reg_json.get("addOwnerGroups"):
        for group in reg_json.get("addOwnerGroups"):
            if group.get("groupSequenceNumber"):
                del group["groupSequenceNumber"]
    return reg_json


def set_group_json(registration, reg_json, current: bool, cleanup: bool = False) -> dict:
    """Build the owner group JSON conditional on current."""
    owner_groups = []
    if registration.owner_groups:
        for group in registration.owner_groups:
            if (current or registration.current_view) and group.status_type in (
                MhrOwnerStatusTypes.ACTIVE,
                MhrOwnerStatusTypes.EXEMPT,
            ):
                owner_groups.append(group.json)
            elif not (current or registration.current_view) and group.registration_id == registration.id:
                owner_groups.append(group.json)
    if current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for group in reg.owner_groups:
                    if group.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                        owner_groups.append(group.json)
    # Sort by group sequence number, remove groupSequenceNumber after sorting.
    reg_json["ownerGroups"] = sort_owner_groups(owner_groups, cleanup)
    return reg_json


def set_transfer_group_json(registration, reg_json, doc_type: str) -> dict:  # pylint: disable=too-many-branches; +1
    """Build the transfer registration owner groups JSON."""
    if not registration.is_transfer() and registration.registration_type != MhrRegistrationTypes.REG_STAFF_ADMIN:
        return reg_json
    if (
        registration.registration_type == MhrRegistrationTypes.REG_STAFF_ADMIN
        and doc_type
        and doc_type
        not in (MhrDocumentTypes.REGC_CLIENT, MhrDocumentTypes.REGC_STAFF, MhrDocumentTypes.PUBA, MhrDocumentTypes.EXRE)
    ):
        return reg_json
    add_groups = []
    delete_groups = []
    if reg_json and registration.owner_groups:
        for group in registration.owner_groups:
            if group.registration_id == registration.id:
                add_groups.append(group.json)
            elif group.change_registration_id == registration.id:
                delete_groups.append(group.json)
    reg_json["addOwnerGroups"] = add_groups
    if registration.change_registrations:
        for reg in registration.change_registrations:
            for existing in reg.owner_groups:
                if existing.registration_id != registration.id and existing.change_registration_id == registration.id:
                    delete_groups.append(existing.json)
    reg_json["deleteOwnerGroups"] = delete_groups
    if reg_json.get("addOwnerGroups"):
        reg_json["addOwnerGroups"] = sort_owner_groups(reg_json.get("addOwnerGroups"), False)
    return reg_json


def update_notes_search_json(notes_json: dict, staff: bool) -> dict:
    """Build the search version of the registration as a json object."""
    if not notes_json:
        return notes_json
    updated_notes = []
    for note in notes_json:
        include: bool = True
        doc_type = note.get("documentType", "")
        if doc_type in ("REG_103", "REG_103E", "STAT", "EXRE", "NCAN", "REG_102", "NRED"):  # Always exclude
            include = False
        elif not staff and doc_type in ("NCON"):  # Always exclude for non-staff
            include = False
        elif not staff and doc_type == "FZE":  # Only staff can see remarks.
            note["remarks"] = ""
        elif (
            not staff
            and doc_type == "REGC"
            and note.get("remarks")
            and note["remarks"] != "MANUFACTURED HOME REGISTRATION CANCELLED"
        ):
            # Only staff can see remarks if not default.
            note["remarks"] = "MANUFACTURED HOME REGISTRATION CANCELLED"
        elif (
            doc_type in ("TAXN", "EXNR", "EXRS", "NPUB", "REST", "CAU", "CAUC", "CAUE")
            and note.get("status") != MhrNoteStatusTypes.ACTIVE
        ):  # Exclude if not active.
            include = False
        elif (
            doc_type in ("CAU", "CAUC", "CAUE")
            and note.get("expiryDateTime")
            and model_utils.date_elapsed(note.get("expiryDateTime"))
        ):  # Exclude if expiry elapsed.
            include = include_caution_note(notes_json, note.get("documentId"))
        if doc_type == "FZE":  # Do not display contact info.
            if note.get("givingNoticeParty"):
                del note["givingNoticeParty"]
        if include:
            updated_notes.append(note)
    return sort_notes(updated_notes)


def update_note_amend_correct(registration, note_json: dict, cancel_reg_id: int) -> dict:
    """Add cancelling registration information if an exemption note is cancelled by a correction or amendment."""
    if not registration.change_registrations:
        return note_json
    for reg in registration.change_registrations:
        if reg.id == cancel_reg_id and reg.documents[0].document_type in (
            MhrDocumentTypes.PUBA,
            MhrDocumentTypes.EXRE,
            MhrDocumentTypes.REGC_CLIENT,
            MhrDocumentTypes.REGC_STAFF,
        ):
            note_json["cancelledDocumentType"] = reg.documents[0].document_type
            note_json["cancelledDocumentDescription"] = get_document_description(reg.documents[0].document_type)
            note_json["cancelledDocumentRegistrationNumber"] = reg.documents[0].document_registration_number
            note_json["cancelledDateTime"] = model_utils.format_ts(reg.registration_ts)
    return note_json


def sort_key_notes_ts(item):
    """Sort the notes registration timestamp."""
    return item.get("createDateTime", "")


def sort_notes(notes):
    """Sort notes by registration timesamp."""
    notes.sort(key=sort_key_notes_ts, reverse=True)
    return notes


def sort_key_groups_sequence(item):
    """Sort the tenants in common owner groups by group sequence number."""
    return item.get("groupSequenceNumber", 1)


def sort_common_owner_groups(owner_groups):
    """Sort tenants in common owner groups by group sequence number."""
    owner_groups.sort(key=sort_key_groups_sequence)
    return owner_groups


def get_notes_json(registration, search: bool, staff: bool = False) -> dict:  # pylint: disable=too-many-branches; 13
    """Fetch all the unit notes for the manufactured home. Search has special conditions on what is included."""
    notes = []
    if not registration.change_registrations:
        return notes
    cancel_notes = []
    for reg in registration.change_registrations:
        if reg.notes and (not search or reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE):
            note = reg.notes[0]
            if note.document_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
                cnote = find_cancelled_note(registration, note.registration_id)
                if cnote:
                    cancel_note = cnote.json
                    cancel_note["ncan"] = note.json
                    cancel_notes.append(cancel_note)
            notes.append(note)
    if not notes:
        return notes
    notes_json = []
    for note in notes:  # Already sorted by timestamp.
        note_json = note.json
        if (
            note_json.get("documentType") in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE)
            and cancel_notes
        ):
            for cnote in cancel_notes:
                if cnote["ncan"].get("documentId") == note_json.get("documentId"):
                    note_json["cancelledDocumentType"] = cnote.get("documentType")
                    note_json["cancelledDocumentDescription"] = cnote.get("documentDescription")
                    note_json["cancelledDocumentRegistrationNumber"] = cnote.get("documentRegistrationNumber")
        elif (
            note_json.get("documentType") in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR)
            and note_json.get("status") == MhrNoteStatusTypes.CANCELLED
            and staff
            and not search
        ):
            # Could be cancelled by correction/amendment - add info if available.
            note_json = update_note_amend_correct(registration, note_json, note.change_registration_id)
        if note_json.get("documentType") not in (
            MhrDocumentTypes.REG_103,
            MhrDocumentTypes.REG_103E,
            MhrDocumentTypes.AMEND_PERMIT,
        ):
            notes_json.append(note_json)
    if search:
        return update_notes_search_json(notes_json, staff)
    return sort_notes(notes_json)


def get_non_staff_notes_json(registration, search: bool):
    """Build the non-BC Registries staff version of the active unit notes as JSON."""
    if search:
        return get_notes_json(registration, search)
    notes = get_notes_json(registration, search)
    if not notes:
        return notes
    updated_notes = []
    for note in notes:
        include: bool = True
        doc_type = note.get("documentType", "")
        if doc_type in (
            MhrDocumentTypes.STAT,
            MhrDocumentTypes.REG_102,  # Always exclude for non-staff
            MhrDocumentTypes.REG_103,
            MhrDocumentTypes.REG_103E,
            MhrDocumentTypes.AMEND_PERMIT,
        ):
            include = False
        elif (
            doc_type in ("TAXN", "EXNR", "EXRS", "NPUB", "REST", "CAU", "CAUC", "CAUE", "NCON")
            and note.get("status") != MhrNoteStatusTypes.ACTIVE
        ):  # Exclude if not active.
            include = False
        elif (
            doc_type in ("CAU", "CAUC", "CAUE")
            and note.get("expiryDateTime")
            and model_utils.date_elapsed(note.get("expiryDateTime"))
        ):  # Exclude if expiry elapsed.
            include = include_caution_note(notes, note.get("documentId"))
        # elif doc_type in ('REG_103', 'REG_103E') and note.get('expiryDateTime') and \
        #        model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
        if include:
            minimal_note = {
                "createDateTime": note.get("createDateTime"),
                "documentType": doc_type,
                "documentDescription": note.get("documentDescription"),
                "status": note.get("status", ""),
            }
            if doc_type in ("REG_103", "REG_103E") and note.get("expiryDateTime"):
                minimal_note["expiryDateTime"] = note.get("expiryDateTime")
            updated_notes.append(minimal_note)
    return updated_notes


def set_note_json(registration, reg_json) -> dict:
    """Build the note JSON for an individual registration that has a unit note."""
    if reg_json and reg_json.get("documentType", "") == MhrDocumentTypes.CANCEL_PERMIT:
        return set_cancel_permit_note(registration, reg_json)
    if reg_json and registration.notes:  # pylint: disable=too-many-nested-blocks; only 1 more.
        reg_note = registration.notes[0].json
        if reg_note.get("documentType") in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
            cnote: MhrNote = find_cancelled_note(registration, registration.id)
            if cnote:
                logger.debug(f"Found cancelled note {cnote.document_type}")
                cnote_json = cnote.json
                reg_note["cancelledDocumentType"] = cnote_json.get("documentType")
                reg_note["cancelledDocumentDescription"] = cnote_json.get("documentDescription")
                reg_note["cancelledDocumentRegistrationNumber"] = cnote_json.get("documentRegistrationNumber")
        reg_json["note"] = reg_note
    return reg_json


def set_cancel_permit_note(registration, reg_json) -> dict:
    """Build the note JSON for a cancelled transport permit note."""
    cnote: MhrNote = find_cancelled_note(registration, registration.id)
    if cnote:
        logger.debug(f"Found cancelled note {cnote.document_type}")
        cnote_json = cnote.json
        note_json = {
            "cancelledDocumentId": cnote_json.get("documentId"),
            "cancelledDocumentType": cnote_json.get("documentType"),
            "cancelledDocumentDescription": cnote_json.get("documentDescription", ""),
            "cancelledDocumentRegistrationNumber": cnote_json.get("documentRegistrationNumber"),
        }
        if registration.change_registrations:
            for reg in registration.change_registrations:
                if reg.id == cnote.registration_id:
                    note_json["cancelledDateTime"] = model_utils.format_ts(reg.registration_ts)
        reg_json["note"] = note_json
    return reg_json


def set_reg_location_json(current_reg, reg_json: dict, reg_id: int) -> dict:
    """Add active location at the time of the registration to the registration JSON ."""
    location = None
    if current_reg.locations:
        loc = current_reg.locations[0]
        if loc.status_type == MhrStatusTypes.ACTIVE or loc.change_registration_id == reg_id:
            location = loc
    if not location and current_reg.change_registrations:
        for reg in current_reg.change_registrations:
            if reg.locations:
                loc = reg.locations[0]
                if loc.status_type == MhrStatusTypes.ACTIVE and loc.registration_id <= reg_id:
                    location = loc
                elif (
                    loc.status_type != MhrStatusTypes.ACTIVE
                    and loc.registration_id <= reg_id <= loc.change_registration_id
                ):
                    location = loc
    if location:
        reg_json["location"] = location.json
    return reg_json


def set_reg_groups_json(  # pylint: disable=too-many-branches
    current_reg, reg_json: dict, reg_id: int, transfer: bool = False
) -> dict:
    """Add active owner_groups at the time of the registration to the registration JSON ."""
    groups = []
    delete_groups = []
    if current_reg.owner_groups:
        for group in current_reg.owner_groups:
            if (
                group.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT)
                or group.registration_id == reg_id
            ):
                groups.append(group.json)
            elif group.change_registration_id == reg_id:
                delete_groups.append(group.json)
    if current_reg.change_registrations:
        for reg in current_reg.change_registrations:
            if reg.owner_groups:
                for group in reg.owner_groups:
                    if (
                        group.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT)
                        and group.registration_id <= reg_id
                    ):
                        groups.append(group.json)
                    elif (
                        group.status_type == MhrOwnerStatusTypes.PREVIOUS
                        and group.registration_id <= reg_id < group.change_registration_id
                    ):
                        groups.append(group.json)
                    if group.status_type == MhrOwnerStatusTypes.PREVIOUS and group.change_registration_id == reg_id:
                        delete_groups.append(group.json)
    if groups and transfer:
        reg_json["addOwnerGroups"] = sort_owner_groups(groups)
    elif groups:
        reg_json["ownerGroups"] = sort_owner_groups(groups)
    if delete_groups and transfer:
        reg_json["deleteOwnerGroups"] = delete_groups
    return reg_json


def set_reg_description_json(current_reg, reg_json: dict, reg_id: int) -> dict:
    """Add active description at the time of the registration to the registration JSON ."""
    description = None
    if current_reg.descriptions:
        desc = current_reg.descriptions[0]
        if desc.status_type == MhrStatusTypes.ACTIVE or desc.change_registration_id == reg_id:
            description = desc
    if not description and current_reg.change_registrations:
        for reg in current_reg.change_registrations:
            if reg.descriptions:
                desc = reg.descriptions[0]
                if desc.status_type == MhrStatusTypes.ACTIVE and desc.registration_id <= reg_id:
                    description = desc
                elif (
                    desc.status_type != MhrStatusTypes.ACTIVE
                    and desc.registration_id <= reg_id <= desc.change_registration_id
                ):
                    description = desc
    if description:
        description_json = description.json
        description_json["sections"] = get_sections_json(current_reg, description.registration_id)
        reg_json["description"] = description_json
    return reg_json


def set_home_status_json(current_reg, reg_json: dict, existing_status: str) -> dict:
    """Set the current home status in the registration JSON ."""
    if (
        current_reg.status_type
        and current_reg.status_type != reg_json.get("status")
        and not (
            current_reg.status_type == MhrRegistrationStatusTypes.ACTIVE
            and reg_json.get("status") == model_utils.STATUS_FROZEN
        )
    ):
        reg_json["status"] = current_reg.status_type
    if existing_status != reg_json.get("status"):
        reg_json["previousStatus"] = existing_status
    return reg_json


def is_identical_owner_name(owner1: dict, owner2: dict) -> bool:
    """Check if 2 owner names are identical ignoring case."""
    if not owner1 or not owner2:
        return False
    if (
        owner1.get("organizationName")
        and owner2.get("organizationName")
        and str(owner1.get("organizationName")).strip().upper() == str(owner2.get("organizationName")).strip().upper()
    ):
        return True
    if owner1.get("individualName") and owner2.get("individualName"):
        if (
            str(owner1["individualName"]["first"]).upper() == str(owner2["individualName"]["first"]).upper()
            and str(owner1["individualName"]["last"]).upper() == str(owner2["individualName"]["last"]).upper()
        ):
            if owner1["individualName"].get("middle", "") == owner2["individualName"].get("middle", ""):
                return True
            if (
                owner1["individualName"].get("middle")
                and owner2["individualName"].get("middle")
                and str(owner1["individualName"]["middle"]).upper() == str(owner2["individualName"]["middle"]).upper()
            ):
                return True
    return False
