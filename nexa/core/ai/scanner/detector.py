import os
import json


class ProjectDetector:
    def detect(self, root_path="."):
        """
        Detect project framework and language.
        Returns:
        {
            "framework": "...",
            "language": "...",
            "confidence": 100,
            "metadata": {}
        }
        """

        def result(framework, language, confidence=100, metadata=None):
            return {
                "framework": framework,
                "language": language,
                "confidence": confidence,
                "metadata": metadata or {}
            }

        # --------------------------------------------------
        # FLUTTER
        # --------------------------------------------------
        if os.path.exists(os.path.join(root_path, "pubspec.yaml")):
            return result(
                "flutter",
                "dart",
                metadata={
                    "mobile": True
                }
            )

        # --------------------------------------------------
        # NEXAPHP
        # --------------------------------------------------
        if (
            (os.path.isdir(os.path.join(root_path, "apps")) and os.path.isdir(os.path.join(root_path, "core")))
            or (os.path.isdir(os.path.join(root_path, "modules")) and os.path.isdir(os.path.join(root_path, "routes")))
        ):
            return result(
                "nexaphp",
                "php"
            )

        # --------------------------------------------------
        # LARAVEL
        # --------------------------------------------------
        if (
            os.path.exists(os.path.join(root_path, "artisan"))
            and os.path.exists(os.path.join(root_path, "composer.json"))
        ):
            return result(
                "laravel",
                "php"
            )

        # --------------------------------------------------
        # CODEIGNITER 3
        # --------------------------------------------------
        if os.path.exists(
            os.path.join(
                root_path,
                "application",
                "config",
                "config.php"
            )
        ):
            return result(
                "codeigniter3",
                "php"
            )

        # --------------------------------------------------
        # DJANGO / DRF
        # --------------------------------------------------
        if os.path.exists(os.path.join(root_path, "manage.py")):

            requirements_files = [
                os.path.join(root_path, "requirements.txt"),
                os.path.join(root_path, "pyproject.toml")
            ]

            content = ""

            for file_path in requirements_files:
                if os.path.exists(file_path):
                    try:
                        with open(
                            file_path,
                            "r",
                            encoding="utf-8"
                        ) as f:
                            content += f.read().lower()
                    except Exception:
                        pass

            if (
                "djangorestframework" in content
                or "rest_framework" in content
            ):
                return result(
                    "django_rest",
                    "python"
                )

            return result(
                "django",
                "python"
            )

        # --------------------------------------------------
        # FASTAPI
        # --------------------------------------------------
        requirements_files = [
            os.path.join(root_path, "requirements.txt"),
            os.path.join(root_path, "pyproject.toml")
        ]

        content = ""

        for file_path in requirements_files:
            if os.path.exists(file_path):
                try:
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:
                        content += f.read().lower()
                except Exception:
                    pass

        if (
            "fastapi" in content
            or "uvicorn" in content
        ):
            return result(
                "fastapi",
                "python"
            )

        # --------------------------------------------------
        # NODE.JS ECOSYSTEM
        # --------------------------------------------------
        package_json_path = os.path.join(
            root_path,
            "package.json"
        )

        if os.path.exists(package_json_path):

            is_typescript = (
                os.path.exists(
                    os.path.join(root_path, "tsconfig.json")
                )
            )

            language = (
                "typescript"
                if is_typescript
                else "javascript"
            )

            try:
                with open(
                    package_json_path,
                    "r",
                    encoding="utf-8"
                ) as f:
                    package_json = json.load(f)

                deps = {}

                deps.update(
                    package_json.get(
                        "dependencies",
                        {}
                    )
                )

                deps.update(
                    package_json.get(
                        "devDependencies",
                        {}
                    )
                )

                # React Native / Expo
                if (
                    "react-native" in deps
                    or "expo" in deps
                ):
                    return result(
                        "react_native",
                        language
                    )

                # Next.js
                if "next" in deps:
                    return result(
                        "nextjs",
                        language
                    )

                # Nuxt
                if "nuxt" in deps:
                    return result(
                        "nuxtjs",
                        language
                    )

                # Vue
                if "vue" in deps:
                    return result(
                        "vuejs",
                        language
                    )

                # Angular
                if "@angular/core" in deps:
                    return result(
                        "angular",
                        language
                    )

                # NestJS
                if "@nestjs/core" in deps:
                    return result(
                        "nestjs",
                        language
                    )

                # Svelte
                if "svelte" in deps:
                    return result(
                        "svelte",
                        language
                    )

                # React
                if "react" in deps:
                    return result(
                        "reactjs",
                        language,
                        metadata={
                            "vite": (
                                os.path.exists(
                                    os.path.join(
                                        root_path,
                                        "vite.config.js"
                                    )
                                )
                                or os.path.exists(
                                    os.path.join(
                                        root_path,
                                        "vite.config.ts"
                                    )
                                )
                            )
                        }
                    )

            except Exception:
                pass

            return result(
                "generic_node",
                language,
                confidence=80
            )

        # --------------------------------------------------
        # GENERIC PHP
        # --------------------------------------------------
        if os.path.exists(
            os.path.join(root_path, "composer.json")
        ):
            return result(
                "generic_php",
                "php",
                confidence=80
            )

        # --------------------------------------------------
        # GENERIC PYTHON
        # --------------------------------------------------
        if (
            os.path.exists(
                os.path.join(root_path, "requirements.txt")
            )
            or os.path.exists(
                os.path.join(root_path, "pyproject.toml")
            )
            or os.path.exists(
                os.path.join(root_path, "setup.py")
            )
        ):
            return result(
                "generic_python",
                "python",
                confidence=80
            )

        # --------------------------------------------------
        # UNKNOWN
        # --------------------------------------------------
        return result(
            "unknown",
            "unknown",
            confidence=0
        )