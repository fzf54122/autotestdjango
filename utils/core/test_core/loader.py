import copy
import logging
import unittest
from typing import List, Union, Tuple
from unittest.loader import TestLoader


class BoleanLoader(TestLoader):

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None, version: str = None,
                 tags: Union[List, Tuple, None] = None):
        suites = super().discover(start_dir, pattern, top_level_dir)
        return self._filter_suites(suites, version, tags)

    def _filter_suites(self, suites, version: str = None, tags: Union[List, Tuple, None] = None):
        suite_list = []

        def wrapper(suite):

            for item in suite:  # suite中包含的是
                if isinstance(item, unittest.TestCase):  # 如果suite中的item包含testcase类
                    # 获取tag和version字段，方便筛选
                    current_class = item.__class__
                    current_class_tags = getattr(current_class, 'tags', None)
                    current_class_versions = getattr(current_class, 'versions', None)
                    if current_class_versions is None or current_class_tags is None:
                        logging.warning(f'tags or versions not found in {current_class}, skipped')
                        break
                    if version in current_class_versions:  # 版本命中，进一步过滤tag
                        if not tags:  # tags 为 None, 不做tag筛选
                            suite_list.append(suite)
                            break
                        common_tags = list(set(current_class_tags) & set(tags))
                        if len(common_tags) == 0:
                            # tags不符合(case 中的tag和提供的tag没取到交集)
                            break
                        else:
                            suite_list.append(suite)
                            break
                    break
                else:
                    wrapper(item)

        wrapper(copy.deepcopy(suites))
        return unittest.TestSuite(suite_list) if suite_list else False
