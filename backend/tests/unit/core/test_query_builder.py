"""
QueryBuilder 单元测试
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from app.core.query_builder import PaginationResult, QueryBuilder, paginate
from sqlalchemy import Column, Integer, String, desc
from sqlalchemy.orm import Query


class MockModel:
    """模拟模型类"""

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(String(20))
    age = Column(Integer)


class TestQueryBuilder:
    """QueryBuilder 测试类"""

    @pytest.fixture
    def mock_query(self):
        """创建模拟 Query 对象"""
        query = MagicMock(spec=Query)
        query.all.return_value = []
        query.first.return_value = None
        query.count.return_value = 0
        return query

    @pytest.fixture
    def builder(self, mock_query):
        """创建 QueryBuilder 实例"""
        return QueryBuilder(mock_query, MockModel)

    def test_init(self, mock_query):
        """测试初始化"""
        builder = QueryBuilder(mock_query, MockModel)

        assert builder.query == mock_query
        assert builder.model_class == MockModel
        assert builder._filters == []
        assert builder._order_by is None

    def test_filter(self, builder, mock_query):
        """测试 filter 方法"""
        result = builder.filter(status="active", name=None)

        assert result == builder
        mock_query.filter.assert_called()

    def test_filter_with_none_value(self, builder, mock_query):
        """测试 filter 方法过滤 None 值"""
        builder.filter(status=None)

        # None 值不应该触发 filter
        mock_query.filter.assert_not_called()

    def test_filter_by(self, builder, mock_query):
        """测试 filter_by 方法"""
        result = builder.filter_by(status="active")

        assert result == builder
        mock_query.filter_by.assert_called_once_with(status="active")

    def test_where(self, builder, mock_query):
        """测试 where 方法"""
        condition = MockModel.id > 1
        result = builder.where(condition)

        assert result == builder
        mock_query.filter.assert_called_once_with(condition)

    def test_where_in(self, builder, mock_query):
        """测试 where_in 方法"""
        result = builder.where_in("status", ["active", "pending"])

        assert result == builder
        mock_query.filter.assert_called_once()

    def test_where_in_empty_values(self, builder, mock_query):
        """测试 where_in 方法空值列表"""
        builder.where_in("status", [])

        mock_query.filter.assert_not_called()

    def test_where_like(self, builder, mock_query):
        """测试 where_like 方法"""
        result = builder.where_like("name", "%test%")

        assert result == builder
        mock_query.filter.assert_called_once()

    def test_where_like_empty_pattern(self, builder, mock_query):
        """测试 where_like 方法空模式"""
        builder.where_like("name", "")

        mock_query.filter.assert_not_called()

    def test_where_between(self, builder, mock_query):
        """测试 where_between 方法"""
        result = builder.where_between("age", 18, 60)

        assert result == builder
        # 由于 MockModel 使用 Column，实际调用可能是1次或2次取决于实现
        assert mock_query.filter.call_count >= 1

    def test_where_between_only_min(self, builder, mock_query):
        """测试 where_between 方法只有最小值"""
        builder.where_between("age", min_value=18)

        mock_query.filter.assert_called_once()

    def test_where_between_only_max(self, builder, mock_query):
        """测试 where_between 方法只有最大值"""
        builder.where_between("age", max_value=60)

        mock_query.filter.assert_called_once()

    def test_order_by_asc(self, builder, mock_query):
        """测试正序排序"""
        result = builder.order_by("id", order_desc=False)

        assert result == builder
        mock_query.order_by.assert_called_once()

    def test_order_by_desc(self, builder, mock_query):
        """测试倒序排序"""
        result = builder.order_by("id", order_desc=True)

        assert result == builder
        mock_query.order_by.assert_called_once()

    def test_paginate(self, builder, mock_query):
        """测试分页"""
        # 配置 mock 链式调用
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query

        result = builder.paginate(page=2, per_page=20)

        assert result == builder
        mock_query.offset.assert_called_once_with(20)  # (2-1) * 20
        mock_query.limit.assert_called_once_with(20)

    def test_paginate_first_page(self, builder, mock_query):
        """测试第一页分页"""
        # 配置 mock 链式调用
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query

        builder.paginate(page=1, per_page=10)

        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)

    def test_offset(self, builder, mock_query):
        """测试 offset 方法"""
        result = builder.offset(50)

        assert result == builder
        mock_query.offset.assert_called_once_with(50)

    def test_limit(self, builder, mock_query):
        """测试 limit 方法"""
        result = builder.limit(100)

        assert result == builder
        mock_query.limit.assert_called_once_with(100)

    def test_join(self, builder, mock_query):
        """测试 join 方法"""
        mock_entity = MagicMock()
        result = builder.join(mock_entity)

        assert result == builder
        mock_query.join.assert_called_once_with(mock_entity)

    def test_options(self, builder, mock_query):
        """测试 options 方法"""
        mock_option = MagicMock()
        result = builder.options(mock_option)

        assert result == builder
        mock_query.options.assert_called_once_with(mock_option)

    def test_execute(self, builder, mock_query):
        """测试 execute 方法"""
        mock_data = [Mock(), Mock()]
        mock_query.all.return_value = mock_data

        result = builder.execute()

        assert result == mock_data
        mock_query.all.assert_called_once()

    def test_first(self, builder, mock_query):
        """测试 first 方法"""
        mock_item = Mock()
        mock_query.first.return_value = mock_item

        result = builder.first()

        assert result == mock_item
        mock_query.first.assert_called_once()

    def test_first_none(self, builder, mock_query):
        """测试 first 方法返回 None"""
        mock_query.first.return_value = None

        result = builder.first()

        assert result is None

    def test_one(self, builder, mock_query):
        """测试 one 方法"""
        mock_item = Mock()
        mock_query.one.return_value = mock_item

        result = builder.one()

        assert result == mock_item

    def test_one_or_none(self, builder, mock_query):
        """测试 one_or_none 方法"""
        mock_item = Mock()
        mock_query.one_or_none.return_value = mock_item

        result = builder.one_or_none()

        assert result == mock_item

    def test_count(self, builder, mock_query):
        """测试 count 方法"""
        mock_query.count.return_value = 100

        result = builder.count()

        assert result == 100
        mock_query.count.assert_called_once()

    def test_exists_true(self, builder, mock_query):
        """测试 exists 方法返回 True"""
        mock_query.first.return_value = Mock()

        result = builder.exists()

        assert result is True

    def test_exists_false(self, builder, mock_query):
        """测试 exists 方法返回 False"""
        mock_query.first.return_value = None

        result = builder.exists()

        assert result is False

    def test_scalar(self, builder, mock_query):
        """测试 scalar 方法"""
        mock_query.scalar.return_value = 42

        result = builder.scalar()

        assert result == 42

    def test_get_query(self, builder, mock_query):
        """测试 get_query 方法"""
        result = builder.get_query()

        assert result == mock_query


class TestPaginationResult:
    """PaginationResult 测试类"""

    def test_init(self):
        """测试初始化"""
        items = [1, 2, 3]
        result = PaginationResult(items, total=100, page=2, per_page=10)

        assert result.items == items
        assert result.total == 100
        assert result.page == 2
        assert result.per_page == 10
        assert result.pages == 10
        assert result.has_prev is True
        assert result.has_next is True

    def test_first_page(self):
        """测试第一页"""
        result = PaginationResult([], total=50, page=1, per_page=10)

        assert result.has_prev is False
        assert result.has_next is True
        assert result.pages == 5

    def test_last_page(self):
        """测试最后一页"""
        result = PaginationResult([], total=50, page=5, per_page=10)

        assert result.has_prev is True
        assert result.has_next is False

    def test_single_page(self):
        """测试只有一页"""
        result = PaginationResult([], total=5, page=1, per_page=10)

        assert result.pages == 1
        assert result.has_prev is False
        assert result.has_next is False

    def test_to_dict(self):
        """测试转换为字典"""
        items = [{"id": 1}, {"id": 2}]
        result = PaginationResult(items, total=20, page=1, per_page=10)

        data = result.to_dict()

        assert data["items"] == items
        assert data["total"] == 20
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["pages"] == 2
        assert data["has_prev"] is False
        assert data["has_next"] is True


class TestPaginateFunction:
    """paginate 函数测试类"""

    def test_paginate(self):
        """测试分页函数"""
        mock_query = MagicMock(spec=Query)
        mock_query.count.return_value = 100
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [1, 2, 3]

        result = paginate(mock_query, page=2, per_page=20)

        assert isinstance(result, PaginationResult)
        assert result.total == 100
        assert result.page == 2
        assert result.per_page == 20
        assert result.items == [1, 2, 3]
        mock_query.offset.assert_called_once_with(20)
        mock_query.limit.assert_called_once_with(20)
