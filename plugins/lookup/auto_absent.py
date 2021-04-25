#!/usr/bin/python

from __future__ import absolute_import, division, print_function
from deepdiff import DeepDiff, extract, grep
from ansible.utils.display import Display

__metaclass__ = type

DOCUMENTATION = """
        lookup: auto_absent
        author: Nathan Mellendorf <nate.mellendorf@gmail.com>
        version_added: "1.0"
        short_description: Diff two YAML structures and return missing keys
        description:
            - Diff two YAML files and return missing keys.
        options:
          _terms:
            description: path(s) of files to read
            required: False
          _old:
            description: Path to the old YAML file to be diffed
            required: True
          _new:
            description: Path to the old YAML file to be diffed
            required: True
          _root:
            description: Root key for the YAML dicts
            required: True
"""
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import yaml
import json

display = Display()


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):

        # 'display.vvv' will be printed when ansible is run with the -vvv flag
        display.vvv(f"Passed in kwargs: {kwargs}")

        old = kwargs.get("old")
        new = kwargs.get("new")

        if not old:
            raise AnsibleError(f"key 'old' was not defined: {old}")
        if not new:
            raise AnsibleError(f"key 'new' was not defined: {new}")

        try:
            with open(f"{new}") as file:
                display.vvv(f"Loading '{new}'...")
                # The SafeLoader parameter handles the conversion from YAML
                # scalar values to Python the dictionary format
                t2 = yaml.load(file, Loader=yaml.SafeLoader)
                display.vvv(f"Complete")

            with open(f"{old}") as file:
                display.vvv(f"Loading '{old}'...")
                # The SafeLoader parameter handles the conversion from YAML
                # scalar values to Python the dictionary format
                t1 = yaml.load(file, Loader=yaml.SafeLoader)
                display.vvv(f"Complete")

            display.vvv(f"Performing DeepDiff...")

            ddiff = DeepDiff(
                t1,  # old config to diff
                t2,  # new config to diff
                ignore_order=True,  # don't consider object positions in config absolute
                view="tree",  # allows us to move up and down the diff tree to get parents
                cutoff_intersection_for_pairs=1,  # diff nested objects too
                verbose_level=2,  # return additional info about the diffs
            )

            display.vvv(f"Complete")

            # create an empty dict to store our diffs in
            new = {}

            display.vvv(f"RAW_DIFF: {ddiff}")

            # if iterable objects were removed...
            if ddiff.get("values_changed"):

                display.vvv(f"Looping over: 'values_changed'")

                # We loop over all objects removed
                # 'x' relates to the current object in the loop
                for x in ddiff.get("values_changed"):

                    if x.t1.get("name") != x.t2.get("name"):
                        display.vvv("> ---")

                        # Update state of new dict
                        x.t1["state"] = "absent"
                        x.up.t2.append(x.t1)

            # if iterable objects were removed...
            if ddiff.get("iterable_item_removed"):

                display.vvv(f"Looping over: 'iterable_item_removed'")

                # We loop over all objects removed
                # 'x' relates to the current object in the loop
                for x in ddiff.get("iterable_item_removed"):
                    display.vvv("> ---")

                    # Update state of new dict
                    x.t1["state"] = "absent"
                    x.up.t2.append(x.t1)

            # if dictionary_item_removed were removed...
            if ddiff.get("dictionary_item_removed"):

                # We loop over all objects removed
                # 'x' relates to the current object in the loop
                for x in ddiff.get("dictionary_item_removed"):
                    display.vvv("> ---")

                    # Update state of new dict
                    x.t1["state"] = "absent"
                    x.up.t2.append(x.up.t1)

            # print(json.dumps(ddiff.t2, indent=4))

            return [ddiff.t2]

        except Exception as e:
            raise AnsibleError(f"{e}")