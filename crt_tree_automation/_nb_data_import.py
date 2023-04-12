from dotenv import load_dotenv
import os
import pynetbox


def _nb_retrieve_records():
    """
    This function simply retrieves the data from Netbox.

    Returns a list of all Netbox record objects for parsing.
    """

    load_dotenv()

    netbox = "https://NETBOX-URL-GOES-HERE/"
    netbox_token = os.environ.get("netbox_token")
    nb = pynetbox.api(netbox, netbox_token)
    nb_records = []

    switches = nb.dcim.devices.filter(role="production-switches", status="active")
    routers = nb.dcim.devices.filter(role="production-routers", status="active")
    firewalls = nb.dcim.devices.filter(role="production-firewalls", status="active")

    nb_records.append(switches)
    nb_records.append(routers)
    nb_records.append(firewalls)

    return nb_records


def _nb_data_dict_builder(nb_records):
    """
    This function organizes the provided data into a packaged dictionary for parsing.

    The output dictionary is called output_dict.
    """
    # Used for tracking unique virtual_chassis instances on Netbox. Filters out stack members.

    output_dict = {}

    vc_list = []

    for record in nb_records:
        for device in record:
            if device.virtual_chassis is None:
                output_dict[device.name] = {
                    "hostname": device.name,
                    "site": device.site.slug,
                    "path": "",
                }

            else:
                vc_name = device.virtual_chassis.name

                if vc_name in vc_list:
                    continue
                else:
                    vc_list.append(vc_name)

                    output_dict[vc_name] = {
                        "hostname": vc_name,
                        "site": device.site.slug,
                        "path": "",
                    }

    return output_dict


def _nb_sitegroup_path_determinator(site, group_data):
    """
    This function is used to determine nested site-group CRT-tree paths.

    It is an extension of _crt_path_generator().
    """

    load_dotenv()

    netbox = "https://NETBOX-URL-GOES-HERE/"
    netbox_token = os.environ.get("netbox_token")
    nb = pynetbox.api(netbox, netbox_token)

    path_end = False
    path = f"{site}/"
    path_prepend = group_data.slug

    while path_end == False:
        path = path_prepend + "/" + path
        sitegroup_data = nb.dcim.site_groups.filter(slug=f"{path_prepend}")

        for sitegroup in sitegroup_data:
            if sitegroup._depth == 0:
                path_end = True
            elif sitegroup._depth > 0:
                path_prepend = sitegroup.parent.slug
                path_end == False

    return path


def _crt_path_generator(output_dict):
    """
    This function checks each device's site for a parent site group.

    Each site group is this recursively evaluated for a higher-level site group until
    a full path is built.

    This value is used to generate the directory structure in the CRT tree.
    """
    # TODO #5

    load_dotenv()

    netbox = "https://NETBOX-URL-GOES-HERE/"
    netbox_token = os.environ.get("netbox_token")
    nb = pynetbox.api(netbox, netbox_token)

    for device in output_dict.keys():
        site = output_dict[device]["site"]

        nb_site_data = nb.dcim.sites.filter(slug=f"{site}")

        for nb_site in nb_site_data:
            if nb_site.group is None:
                path = f"{site}/"
            else:
                path = _nb_sitegroup_path_determinator(site, nb_site.group)

        output_dict[device]["path"] = path

    return output_dict


def _nb_data_import():
    """
    This function is for retrieving all active devices from Netbox
    and returning the data as a parsable format for CRT automation.
    """

    nb_records = _nb_retrieve_records()

    nb_data_dict = _nb_data_dict_builder(nb_records)

    output_dict = _crt_path_generator(nb_data_dict)

    return output_dict
