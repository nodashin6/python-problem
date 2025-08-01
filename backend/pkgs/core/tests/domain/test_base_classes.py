"""
Tests for Core Domain Base Classes
コアドメイン基底クラスのテスト
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from ppcore.domain.base import BaseEntity, BaseModel, BaseValueObject


class TestBaseValueObject:
    """Test BaseValueObject functionality"""

    def test_creation(self):
        """Test value object creation"""
        
        class TestValueObject(BaseValueObject):
            name: str
            value: int
        
        obj = TestValueObject(name="test", value=42)
        assert obj.name == "test"
        assert obj.value == 42

    def test_immutability(self):
        """Test that value objects are immutable"""
        
        class TestValueObject(BaseValueObject):
            name: str
        
        obj = TestValueObject(name="test")
        
        with pytest.raises(ValueError, match=".*frozen.*"):
            obj.name = "new_name"

    def test_equality(self):
        """Test value object equality"""
        
        class TestValueObject(BaseValueObject):
            name: str
            value: int
        
        obj1 = TestValueObject(name="test", value=42)
        obj2 = TestValueObject(name="test", value=42)
        obj3 = TestValueObject(name="different", value=42)
        
        assert obj1 == obj2
        assert obj1 != obj3


class TestBaseEntity:
    """Test BaseEntity functionality"""

    def test_creation_with_defaults(self):
        """Test entity creation with default values"""
        entity = BaseEntity()
        
        assert isinstance(entity.id, UUID)
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)

    def test_creation_with_values(self):
        """Test entity creation with provided values"""
        test_id = uuid4()
        test_time = datetime.now()
        
        entity = BaseEntity(
            id=test_id,
            created_at=test_time,
            updated_at=test_time
        )
        
        assert entity.id == test_id
        assert entity.created_at == test_time
        assert entity.updated_at == test_time

    def test_get_id(self):
        """Test get_id method"""
        entity = BaseEntity()
        assert entity.get_id() == entity.id

    def test_mutability(self):
        """Test that entities are mutable"""
        entity = BaseEntity()
        original_time = entity.updated_at
        
        # Should be able to update
        new_time = datetime.now()
        entity.updated_at = new_time
        assert entity.updated_at == new_time
        assert entity.updated_at != original_time


class TestBaseModel:
    """Test BaseModel functionality"""

    def test_abstract_class(self):
        """Test that BaseModel is abstract"""
        with pytest.raises(TypeError):
            BaseModel()

    def test_concrete_implementation(self):
        """Test concrete BaseModel implementation"""
        
        class TestModel(BaseModel):
            name: str
            
        test_id = uuid4()
        test_time = datetime.now()
        
        model = TestModel(
            id=test_id,
            created_at=test_time,
            updated_at=test_time,
            name="test"
        )
        
        assert model.id == test_id
        assert model.name == "test"
        assert model.get_id() == test_id

    def test_to_dict(self):
        """Test to_dict method"""
        
        class TestModel(BaseModel):
            name: str
            value: int
            
        model = TestModel(
            id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="test",
            value=42
        )
        
        result = model.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 42
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result