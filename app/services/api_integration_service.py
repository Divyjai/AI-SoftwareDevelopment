from app.domain.models.frontend_plan import APIContract
from typing import List, Dict, Any

class APIIntegrationService:
    def generate_api_clients(self, api_contracts: List[APIContract]) -> List[Dict[str, Any]]:
        files = []
        
        # Base API Client setup
        base_client = """import axios from 'axios';
export const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
});
"""
        files.append({"path": "lib/api_client.ts", "content": base_client})
        
        # Generate hooks per contract
        hooks_content = "import { apiClient } from './api_client';\nimport { useQuery, useMutation } from '@tanstack/react-query';\n\n"
        for contract in api_contracts:
            endpoint = contract.endpoint
            func_name = endpoint.replace("/", "_").strip("_")
            if not func_name:
                continue
                
            hooks_content += f"export const use{func_name.title()} = () => {{\n"
            hooks_content += f"  return useQuery({['{func_name}'] }, () => apiClient.get('{endpoint}').then(res => res.data));\n"
            hooks_content += "};\n\n"
            
        files.append({"path": "hooks/useApi.ts", "content": hooks_content})
        
        return files
