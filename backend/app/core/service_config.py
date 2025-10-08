"""Simplified service configuration system for Pinecone-only setup."""

from typing import Dict, Any, Optional
from enum import Enum
from loguru import logger
from core.config import settings


class ServiceProvider(Enum):
    """Available service providers for each component."""
    
    # Vector Stores
    PINECONE = "pinecone"
    
    MEMORY = "memory"
    MEMORY_DB = "memory"


class ServiceConfiguration:
    """Service configuration manager for Pinecone-only setup."""
    
    # Simplified configurations for session-based processing
    CONFIGURATIONS = {
        "development": {
            "vector_store": ServiceProvider.PINECONE,
            "storage": ServiceProvider.MEMORY,
            "database": ServiceProvider.MEMORY_DB,
            "description": "Development setup with Pinecone vector store - session-based processing"
        },
        
        "production": {
            "vector_store": ServiceProvider.PINECONE,
            "storage": ServiceProvider.MEMORY,
            "database": ServiceProvider.MEMORY_DB,
            "description": "Production setup with Pinecone vector store - session-based processing"
        }
    }
    
    @classmethod
    def get_configuration(cls, config_name: str) -> Dict[str, Any]:
        """Get predefined configuration by name."""
        if config_name not in cls.CONFIGURATIONS:
            available = ", ".join(cls.CONFIGURATIONS.keys())
            raise ValueError(f"Unknown configuration '{config_name}'. Available: {available}")
        
        return cls.CONFIGURATIONS[config_name]
    
    @classmethod
    def list_configurations(cls) -> Dict[str, str]:
        """List all available configurations with descriptions."""
        return {name: config["description"] for name, config in cls.CONFIGURATIONS.items()}
    
    @classmethod
    def apply_configuration(cls, config_name: str) -> None:
        """Apply a predefined configuration to settings."""
        config = cls.get_configuration(config_name)
        
        settings.vector_store_type = config["vector_store"].value
        settings.storage_type = config["storage"].value
        settings.database_type = config["database"].value
        
        logger.info(f"Applied '{config_name}' configuration: {config['description']}")
    
    @classmethod
    def get_current_configuration(cls) -> Dict[str, Any]:
        """Get current configuration based on settings."""
        return {
            "vector_store": settings.vector_store_type,
            "storage": settings.storage_type,
            "database": settings.database_type,
            "environment": settings.environment
        }
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate current configuration and return status."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "services": {}
        }
        
        vector_store_status = cls._validate_vector_store()
        validation_result["services"]["vector_store"] = vector_store_status
        
        storage_status = {"valid": True, "errors": [], "warnings": []}
        validation_result["services"]["storage"] = storage_status
        
        database_status = {"valid": True, "errors": [], "warnings": []}
        validation_result["services"]["database"] = database_status
        
        for service, status in validation_result["services"].items():
            if not status["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(status["errors"])
            validation_result["warnings"].extend(status.get("warnings", []))
        
        return validation_result
    
    @classmethod
    def _validate_vector_store(cls) -> Dict[str, Any]:
        """Validate vector store configuration."""
        status = {"valid": True, "errors": [], "warnings": []}
        
        vector_store_type = settings.vector_store_type.lower()
        
        if vector_store_type == "pinecone":
            if not settings.pinecone_api_key:
                status["valid"] = False
                status["errors"].append("Pinecone API key is required")
        else:
            status["valid"] = False
            status["errors"].append("Only Pinecone vector store is supported")
        
        return status


class ServiceSwitcher:
    """Utility class for switching between service providers."""
    
    @staticmethod
    def switch_to_development_config() -> None:
        """Switch to development configuration."""
        ServiceConfiguration.apply_configuration("development")
        logger.info("Switched to development configuration - Pinecone with session-based processing")
    
    @staticmethod
    def switch_to_production_config() -> None:
        """Switch to production configuration."""
        ServiceConfiguration.apply_configuration("production")
        logger.info("Switched to production configuration - Pinecone with session-based processing")
    
    @staticmethod
    def get_cost_estimate() -> Dict[str, Any]:
        """Get cost estimate for current configuration."""
        current_config = ServiceConfiguration.get_current_configuration()
        
        cost_estimates = {
            "vector_store": {
                "pinecone": {"cost": "$0-70", "description": "Free tier + usage-based pricing"}
            },
            "storage": {
                "memory": {"cost": "$0", "description": "In-memory processing - no storage costs"}
            },
            "database": {
                "memory": {"cost": "$0", "description": "In-memory processing - no database costs"}
            }
        }
        
        return {
            "current_configuration": current_config,
            "cost_breakdown": {
                "vector_store": cost_estimates["vector_store"].get(current_config["vector_store"], {}),
                "storage": cost_estimates["storage"].get(current_config["storage"], {}),
                "database": cost_estimates["database"].get(current_config["database"], {})
            },
            "total_estimated_cost": "$0-70/month (Pinecone free tier + usage)",
            "note": "Documents are processed in-memory and not permanently stored. Only vector embeddings are stored in Pinecone."
        }


# Convenience functions for easy configuration switching
def use_development_setup():
    """Switch to development setup."""
    ServiceSwitcher.switch_to_development_config()

def use_production_setup():
    """Switch to production setup."""
    ServiceSwitcher.switch_to_production_config()

def validate_current_setup():
    """Validate current setup and return status."""
    return ServiceConfiguration.validate_configuration()

def get_cost_estimate():
    """Get cost estimate for current setup."""
    return ServiceSwitcher.get_cost_estimate()
