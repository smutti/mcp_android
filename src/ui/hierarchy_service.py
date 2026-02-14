import xml.etree.ElementTree as ET


class HierarchyService:
    """Retrieves and filters uiautomator hierarchy dumps."""

    @staticmethod
    def get_filtered_dump(u2_device, attributes_to_keep: list[str]) -> str:
        xml_dump = u2_device.dump_hierarchy(compressed=False)
        root = ET.fromstring(xml_dump)

        for node in root.iter():
            existing_attrs = list(node.attrib)
            for attribute in existing_attrs:
                if attribute not in attributes_to_keep:
                    del node.attrib[attribute]

        return ET.tostring(root, encoding="unicode")
