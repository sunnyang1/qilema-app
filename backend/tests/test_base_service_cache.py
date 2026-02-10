"""
BaseService缓存机制单元测试
"""
import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# 创建测试用的内存数据库
Base = declarative_base()


class TestModel(Base):
    """测试模型"""
    __tablename__ = "test_models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    value = Column(Integer)
    
    def to_dict(self):
        return {"id": self.id, "name": self.name, "value": self.value}


class TestBaseServiceCache:
    """测试BaseService缓存机制"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库会话"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def test_service(self):
        """创建测试服务类"""
        from app.services.base_service import BaseService
        
        class TestService(BaseService[TestModel]):
            model_class = TestModel
            cache_prefix = "test"
            cache_ttl = 60
        
        return TestService
    
    def test_create_and_get_by_id(self, db, test_service):
        """测试创建记录并通过ID获取（使用缓存）"""
        # 创建记录
        record = test_service.create_record(db, {"name": "测试1", "value": 100})
        record_id = record.id
        
        # 清除会话缓存，模拟新请求
        db.expunge_all()
        
        # 通过ID获取（应该使用缓存）
        cached_record = test_service.get_by_id(db, record_id)
        
        assert cached_record is not None
        assert cached_record.id == record_id
        assert cached_record.name == "测试1"
        assert cached_record.value == 100
    
    def test_update_invalidates_cache(self, db, test_service):
        """测试更新操作使缓存失效"""
        # 创建记录
        record = test_service.create_record(db, {"name": "测试", "value": 100})
        record_id = record.id
        
        # 获取一次（放入缓存）
        original = test_service.get_by_id(db, record_id)
        
        # 更新记录
        test_service.update_record(db, record_id, {"name": "已更新", "value": 200})
        
        # 清除会话缓存
        db.expunge_all()
        
        # 再次获取（应该从数据库获取最新值）
        updated = test_service.get_by_id(db, record_id)
        
        assert updated.name == "已更新"
        assert updated.value == 200
    
    def test_delete_invalidates_cache(self, db, test_service):
        """测试删除操作使缓存失效"""
        # 创建记录
        record = test_service.create_record(db, {"name": "测试", "value": 100})
        record_id = record.id
        
        # 获取一次（放入缓存）
        original = test_service.get_by_id(db, record_id)
        assert original is not None
        
        # 删除记录
        result = test_service.delete_record(db, record_id)
        assert result is True
        
        # 再次获取（应该返回None）
        deleted = test_service.get_by_id(db, record_id)
        assert deleted is None
    
    def test_list_records_with_filters(self, db, test_service):
        """测试带过滤条件的列表查询"""
        # 创建多条记录
        test_service.create_record(db, {"name": "A", "value": 1})
        test_service.create_record(db, {"name": "B", "value": 2})
        test_service.create_record(db, {"name": "A", "value": 3})
        
        # 按name过滤
        results = test_service.list_records(db, name="A")
        
        assert len(results) == 2
        assert all(r.name == "A" for r in results)
    
    def test_list_records_with_pagination(self, db, test_service):
        """测试列表分页"""
        # 创建10条记录
        for i in range(10):
            test_service.create_record(db, {"name": f"测试{i}", "value": i})
        
        # 获取第1页，每页3条
        page1 = test_service.list_records(db, skip=0, limit=3)
        assert len(page1) == 3
        
        # 获取第2页
        page2 = test_service.list_records(db, skip=3, limit=3)
        assert len(page2) == 3
    
    def test_list_records_with_ordering(self, db, test_service):
        """测试列表排序"""
        # 创建记录（不按顺序）
        test_service.create_record(db, {"name": "C", "value": 3})
        test_service.create_record(db, {"name": "A", "value": 1})
        test_service.create_record(db, {"name": "B", "value": 2})
        
        # 升序排列
        results = test_service.list_records(db, order_by="name", order_desc=False)
        names = [r.name for r in results]
        assert names == ["A", "B", "C"]
        
        # 降序排列
        results = test_service.list_records(db, order_by="name", order_desc=True)
        names = [r.name for r in results]
        assert names == ["C", "B", "A"]
    
    def test_count_records(self, db, test_service):
        """测试记录计数"""
        # 创建记录
        test_service.create_record(db, {"name": "A", "value": 1})
        test_service.create_record(db, {"name": "A", "value": 2})
        test_service.create_record(db, {"name": "B", "value": 3})
        
        # 计数所有记录
        total = test_service.count_records(db)
        assert total == 3
        
        # 按条件计数
        count_a = test_service.count_records(db, name="A")
        assert count_a == 2
    
    def test_get_by_field(self, db, test_service):
        """测试根据字段获取单条记录"""
        # 创建记录
        test_service.create_record(db, {"name": "测试", "value": 100})
        
        # 通过name获取
        result = test_service.get_by_field(db, "name", "测试")
        
        assert result is not None
        assert result.name == "测试"
        assert result.value == 100
        
        # 获取不存在的记录
        not_found = test_service.get_by_field(db, "name", "不存在")
        assert not_found is None
    
    def test_cache_isolation_between_services(self, db):
        """测试不同服务之间的缓存隔离"""
        from app.services.base_service import BaseService
        
        class ServiceA(BaseService[TestModel]):
            model_class = TestModel
            cache_prefix = "service_a"
        
        class ServiceB(BaseService[TestModel]):
            model_class = TestModel
            cache_prefix = "service_b"
        
        # ServiceA创建记录
        record = ServiceA.create_record(db, {"name": "A", "value": 1})
        
        # 两个服务应该都能获取到同一条记录
        from_a = ServiceA.get_by_id(db, record.id)
        from_b = ServiceB.get_by_id(db, record.id)
        
        assert from_a is not None
        assert from_b is not None
        assert from_a.id == from_b.id
