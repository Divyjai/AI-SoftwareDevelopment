class ComponentGenerator:
    def generate(self, plan_components, context):
        files = []
        for comp in plan_components:
            name = comp.get("name")
            comp_type = comp.get("type", "client")
            # In a real implementation this would fetch from component catalog
            content = f"// {name} Component ({comp_type})\nexport function {name}() {{ return <div />; }}"
            files.append({"path": f"components/ui/{name.lower()}.tsx", "content": content})
        return files

class RouteGenerator:
    def generate(self, plan_pages, context):
        files = []
        for page in plan_pages:
            path = page.get("path")
            if path == "/":
                file_path = "app/page.tsx"
            else:
                file_path = f"app{path}/page.tsx"
            content = f"export default function Page() {{ return <div>{path}</div>; }}"
            files.append({"path": file_path, "content": content})
        return files

class ThemeGenerator:
    def generate(self, theme_config, context):
        # Generate tailwind.config.ts and globals.css based on theme
        return [
            {"path": "tailwind.config.ts", "content": "// Tailwind config based on plan"},
            {"path": "app/globals.css", "content": "/* Global CSS */"}
        ]

class LayoutGenerator:
    def generate(self, layouts, context):
        files = []
        for layout in layouts:
            # layout might be string or dict
            name = layout if isinstance(layout, str) else layout.get("name", "layout")
            content = "export default function Layout({children}) { return <div>{children}</div>; }"
            files.append({"path": f"app/layout.tsx", "content": content}) # Simplified
        return files
