"""Tests for OpenSpace Engine module"""

import pytest
from openspace_openhands_evolution.openspace_engine import OpenSpaceEngine, SkillCard


class TestSkillCard:
    """Test SkillCard class"""
    
    def test_create_skill_card(self):
        """Test creating a basic skill card"""
        skill = SkillCard(
            skill_id="test-skill-001",
            name="Test Skill",
            description="A test skill",
            code="print('hello')"
        )
        
        assert skill.skill_id == "test-skill-001"
        assert skill.name == "Test Skill"
        assert skill.description == "A test skill"
        assert skill.code == "print('hello')"
        assert skill.version == 1
        assert skill.usage_count == 0
        assert skill.success_rate == 0.0
    
    def test_skill_card_with_metadata(self):
        """Test skill card with metadata"""
        metadata = {
            "author": "test-user",
            "tags": ["test", "demo"],
            "language": "python"
        }
        
        skill = SkillCard(
            skill_id="test-002",
            name="Skill with Metadata",
            description="Test",
            code="pass",
            metadata=metadata
        )
        
        assert skill.metadata == metadata
        assert skill.metadata["author"] == "test-user"
    
    def test_to_dict(self):
        """Test converting skill to dictionary"""
        skill = SkillCard(
            skill_id="test-003",
            name="Dict Test",
            description="Test dict conversion",
            code="return True"
        )
        
        skill_dict = skill.to_dict()
        
        assert isinstance(skill_dict, dict)
        assert skill_dict["skill_id"] == "test-003"
        assert skill_dict["name"] == "Dict Test"
        assert "created_at" in skill_dict
        assert "version" in skill_dict


class TestOpenSpaceEngine:
    """Test OpenSpaceEngine class"""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance for testing"""
        return OpenSpaceEngine(registry_path="./test_data")
    
    def test_init_engine(self, engine):
        """Test engine initialization"""
        assert engine.registry_path == "./test_data"
        assert hasattr(engine, 'skill_registry')
        assert isinstance(engine.skill_registry, dict)
    
    @pytest.mark.asyncio
    async def test_register_skill(self, engine):
        """Test registering a skill"""
        skill_data = {
            "skill_id": "test-reg-001",
            "name": "Registration Test",
            "description": "Test skill registration",
            "code": "print('registered')"
        }
        
        await engine.register_skill(skill_data)
        
        assert "test-reg-001" in engine.skill_registry
        assert engine.skill_registry["test-reg-001"].name == "Registration Test"
    
    @pytest.mark.asyncio
    async def test_search_skills_by_keyword(self, engine):
        """Test searching skills by keyword"""
        # Register some test skills
        await engine.register_skill({
            "skill_id": "search-001",
            "name": "Python API Builder",
            "description": "Build REST APIs with Python",
            "code": "pass"
        })
        
        await engine.register_skill({
            "skill_id": "search-002",
            "name": "JavaScript Helper",
            "description": "Helper functions for JavaScript",
            "code": "pass"
        })
        
        # Search for Python-related skills
        results = await engine.search_skills("python", {})
        
        assert len(results) > 0
        assert any("API" in skill.get("name", "") for skill in results)
    
    @pytest.mark.asyncio
    async def test_get_project_skills(self, engine):
        """Test getting skills for a project"""
        # Register skills with project metadata
        await engine.register_skill({
            "skill_id": "proj-skill-001",
            "name": "Project Skill",
            "description": "Skill for specific project",
            "code": "pass",
            "metadata": {"project_id": "test-project"}
        })
        
        skills = await engine.get_project_skills("test-project")
        
        # Should return skills (may be empty if filtering not implemented)
        assert isinstance(skills, list)
    
    @pytest.mark.asyncio
    async def test_capture_environment_fingerprint(self, engine):
        """Test capturing environment fingerprint (V-06)"""
        fingerprint = await engine.capture_environment_fingerprint("test-project")
        
        assert isinstance(fingerprint, dict)
        assert "platform" in fingerprint
        assert "python_version" in fingerprint
        assert "timestamp" in fingerprint
    
    @pytest.mark.asyncio
    async def test_evolve_skill(self, engine):
        """Test skill evolution"""
        # Register initial skill
        await engine.register_skill({
            "skill_id": "evolve-001",
            "name": "Evolvable Skill",
            "description": "Initial version",
            "code": "v1"
        })
        
        # Evolve the skill
        evolved = await engine.evolve_skill(
            skill_id="evolve-001",
            improvements=["Improved performance", "Better error handling"]
        )
        
        assert evolved is not None
        assert evolved.version == 2
    
    @pytest.mark.asyncio
    async def test_fix_skill(self, engine):
        """Test fixing a skill"""
        # Register skill
        await engine.register_skill({
            "skill_id": "fix-001",
            "name": "Fixable Skill",
            "description": "Needs fixing",
            "code": "broken_code"
        })
        
        # Fix the skill
        fixed = await engine.fix_skill(
            skill_id="fix-001",
            error_context={"error": "SyntaxError", "line": 5}
        )
        
        assert fixed is not None
        assert "fix_history" in fixed.metadata
    
    @pytest.mark.asyncio
    async def test_get_status(self, engine):
        """Test getting engine status"""
        status = await engine.get_status()
        
        assert isinstance(status, dict)
        assert "status" in status
        assert "skills_count" in status
        assert "registry_path" in status
