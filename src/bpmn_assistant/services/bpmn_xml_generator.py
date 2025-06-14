import json
import xml.etree.ElementTree as ET

from bpmn_assistant.config import logger
from bpmn_assistant.services import BpmnProcessTransformer


class BpmnXmlGenerator:
    """
    Class to generate BPMN XML from the BPMN process data in JSON format.
    """

    def __init__(self):
        self.transformer = BpmnProcessTransformer()

    def create_bpmn_xml(self, process: list[dict]) -> str:
        """
        Create BPMN XML from the process data.
        Args:
            process: BPMN process structure generated by the LLM.
        Returns:
            The BPMN XML string.
        """
        logger.info('Starting to create BPMN XML from process: %s', process)
        transformed_process = self.transformer.transform(process)
        logger.debug(
            f"Transformed process:\n{json.dumps(transformed_process, indent=2)}"
        )

        # Create the root element (definitions)
        root = ET.Element("definitions")
        root.set("xmlns", "http://www.omg.org/spec/BPMN/20100524/MODEL")
        root.set("xmlns:bpmndi", "http://www.omg.org/spec/BPMN/20100524/DI")
        root.set("xmlns:dc", "http://www.omg.org/spec/DD/20100524/DC")
        root.set("xmlns:di", "http://www.omg.org/spec/DD/20100524/DI")
        root.set("id", "definitions_1")

        # Create the process element
        process_element = ET.SubElement(root, "process")
        process_element.set("id", "Process_1")
        process_element.set("isExecutable", "false")

        # Add elements
        for element in transformed_process["elements"]:
            elem = ET.SubElement(process_element, element["type"])
            elem.set("id", element["id"])

            # Add label if it exists
            if element["label"]:
                elem.set("name", element["label"])

            # Add incoming and outgoing flows as child elements
            for incoming in element["incoming"]:
                ET.SubElement(elem, "incoming").text = incoming
            for outgoing in element["outgoing"]:
                ET.SubElement(elem, "outgoing").text = outgoing

        # Add flows
        for flow in transformed_process["flows"]:
            seq_flow = ET.SubElement(process_element, "sequenceFlow")
            seq_flow.set("id", flow["id"])
            seq_flow.set("sourceRef", flow["sourceRef"])
            seq_flow.set("targetRef", flow["targetRef"])

            # Add condition if it exists
            if flow["condition"]:
                seq_flow.set("name", flow["condition"])

        xml_string = ET.tostring(root, encoding="unicode")
        logger.info('Generated BPMN XML: %s', xml_string)
        return xml_string
