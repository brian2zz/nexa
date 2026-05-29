import os
import subprocess
from nexa.core.runtime.command import BaseCommand

# Template content dictionary with correct package: prefixing
TEMPLATES = {
    "app_navigator": """import 'package:flutter/material.dart';

class AppNavigator {
  static final GlobalKey<NavigatorState> navigatorKey =
      GlobalKey<NavigatorState>();
}
""",

    "session_provider": """import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{package_name}/core/services/session_service.dart';

final sessionServiceProvider = Provider<SessionService>((ref) => SessionService());
""",

    "session_service": """import 'package:shared_preferences/shared_preferences.dart';

class SessionService {
  static const String _keyToken = 'auth_token';

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyToken, token);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyToken);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
""",

    "http_service": """import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:{package_name}/core/utils/app_constants.dart';

class HttpService {{
  final Dio _dio;
  final bool isPrint;

  HttpService({{Map<String, dynamic>? defaultHeaders, this.isPrint = false}})
    : _dio = Dio(
        BaseOptions(
          baseUrl: AppConstants.baseUrl,
          connectTimeout: const Duration(seconds: 10),
          headers: defaultHeaders ?? {{}},
        ),
      ) {{
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {{
        options.extra['startTime'] = DateTime.now().millisecondsSinceEpoch;
        return handler.next(options);
      }},
      onResponse: (response, handler) {{
        final startTime = response.requestOptions.extra['startTime'] as int?;
        final duration = startTime != null
            ? DateTime.now().millisecondsSinceEpoch - startTime
            : 0;
        print('[NEXA_NET] ${{response.requestOptions.method}} ${{response.requestOptions.path}} ${{response.statusCode}} ${{duration}}ms');
        return handler.next(response);
      }},
      onError: (e, handler) {{
        final startTime = e.requestOptions.extra['startTime'] as int?;
        final duration = startTime != null
            ? DateTime.now().millisecondsSinceEpoch - startTime
            : 0;
        print('[NEXA_NET] ${{e.requestOptions.method}} ${{e.requestOptions.path}} ${{e.response?.statusCode ?? "ERROR"}} ${{duration}}ms');
        return handler.next(e);
      }},
    ));
  }}

  Future<Response> request(
    String endpoint, {{
    String method = 'GET',
    Map<String, dynamic>? headers,
    Map<String, dynamic>? queryParameters,
    dynamic data,
    String? overrideBaseUrl,
  }}) async {{
    try {{
      final response = await _dio.request(
        "${{overrideBaseUrl ?? _dio.options.baseUrl}}$endpoint",
        options: Options(method: method, headers: headers),
        queryParameters: queryParameters,
        data: data,
      );
      return response;
    } on DioException catch (e) {{
      String errorMessage = e.message ?? "Unknown error";
      throw Exception('HTTP error: ${{e.response?.statusCode}} $errorMessage');
    }}
  }}
}}
""",

    "size_utils": """import 'package:flutter/material.dart';

// ignore: deprecated_member_use
Size size =
    WidgetsBinding.instance.window.physicalSize /
    // ignore: deprecated_member_use
    WidgetsBinding.instance.window.devicePixelRatio;

const num FIGMA_DESIGN_WIDTH = 428;
const num FIGMA_DESIGN_HEIGHT = 926;
const num FIGMA_DESIGN_STATUS_BAR = 47;

get width => size.width;

get height {
  num statusBar = MediaQueryData.fromWindow(
    WidgetsBinding.instance.window,
  ).viewPadding.top;
  num bottomBar = MediaQueryData.fromWindow(
    WidgetsBinding.instance.window,
  ).viewPadding.bottom;
  num screenHeight = size.height - statusBar - bottomBar;
  return screenHeight;
}

double getHorizontalSize(double px) {
  return ((px * width) / FIGMA_DESIGN_WIDTH);
}

double getVerticalSize(double px) {
  return ((px * height) / (FIGMA_DESIGN_HEIGHT - FIGMA_DESIGN_STATUS_BAR));
}

double getSize(double px) {
  var height = getVerticalSize(px);
  var width = getHorizontalSize(px);
  return height < width ? height.toDouble() : width.toDouble();
}

double getFontSize(double px) {
  return getSize(px);
}

EdgeInsetsGeometry getPadding({
  double? all,
  double? left,
  double? top,
  double? right,
  double? bottom,
}) {
  return getMarginOrPadding(
    all: all,
    left: left,
    top: top,
    right: right,
    bottom: bottom,
  );
}

EdgeInsetsGeometry getMargin({
  double? all,
  double? left,
  double? top,
  double? right,
  double? bottom,
}) {
  return getMarginOrPadding(
    all: all,
    left: left,
    top: top,
    right: right,
    bottom: bottom,
  );
}

EdgeInsetsGeometry getMarginOrPadding({
  double? all,
  double? left,
  double? top,
  double? right,
  double? bottom,
}) {
  if (all != null) {
    left = all;
    top = all;
    right = all;
    bottom = all;
  }
  return EdgeInsets.only(
    left: getHorizontalSize(left ?? 0),
    top: getVerticalSize(top ?? 0),
    right: getHorizontalSize(right ?? 0),
    bottom: getVerticalSize(bottom ?? 0),
  );
}

class ResponsiveLayout {
  static const double mobileMaxWidth = 600;
  static const double tabletMaxWidth = 1024;

  static bool isMobile(BuildContext context) =>
      MediaQuery.of(context).size.width < mobileMaxWidth;

  static bool isTablet(BuildContext context) =>
      MediaQuery.of(context).size.width >= mobileMaxWidth &&
      MediaQuery.of(context).size.width < tabletMaxWidth;

  static bool isDesktop(BuildContext context) =>
      MediaQuery.of(context).size.width >= tabletMaxWidth;

  static bool isPortrait(BuildContext context) =>
      MediaQuery.of(context).orientation == Orientation.portrait;

  static bool isLandscape(BuildContext context) =>
      MediaQuery.of(context).orientation == Orientation.landscape;
}

class ResponsiveWidget extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveWidget({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    if (ResponsiveLayout.isDesktop(context) && desktop != null) {
      return desktop!;
    } else if (ResponsiveLayout.isTablet(context) && tablet != null) {
      return tablet!;
    } else {
      return mobile;
    }
  }
}
""",

    "app_constants": """class AppConstants {{
  static const String baseUrl = 'http://127.0.0.1:8000/api';
  static const String appName = '{project_name}';
}}
""",

    "app_dimensions": """class AppDimensions {
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  
  static const double radiusSmall = 4.0;
  static const double radiusMedium = 8.0;
  static const double radiusLarge = 16.0;
}
""",

    "color_constants": """import 'package:flutter/material.dart';

class AppColors {
  static const Color primary = Color(0xFFFF5E3A); // Sleek modern coral
  static const Color secondary = Color(0xFF1F2937); // Premium dark charcoal
  static const Color appSecondaryBackground = Color(0xFFF3F4F6); // Soft gray
  static const Color textPrimary = Color(0xFF111827);
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color gray400 = Color(0xFF9CA3AF);
}
""",

    "app_theme": """import 'package:flutter/material.dart';
import 'package:{package_name}/core/utils/color_constants.dart';

class AppTheme {
  static ThemeData lightTheme = ThemeData(
    primaryColor: AppColors.primary,
    scaffoldBackgroundColor: AppColors.appSecondaryBackground,
    textTheme: AppTypography.textTheme,
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      iconTheme: IconThemeData(color: Colors.black),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: AppColors.gray400),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: AppColors.primary, width: 2),
      ),
    ),
  );
}

class AppTypography {
  static const TextStyle headline1 = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    letterSpacing: -1.5,
    color: Colors.black,
  );

  static const TextStyle headline2 = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.5,
    color: Colors.black,
  );

  static const TextStyle body1 = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: Colors.black,
  );

  static const TextStyle body2 = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: Colors.black,
  );

  static const TextStyle caption = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w300,
    color: Colors.black54,
  );

  static TextTheme textTheme = const TextTheme(
    headlineLarge: headline1,
    headlineMedium: headline2,
    bodyLarge: body1,
    bodyMedium: body2,
    bodySmall: caption,
  );

  static TextStyle boldTextStyle({
    double size = 14,
    Color color = Colors.black,
    double letterSpacing = 0.2,
  }) {
    return TextStyle(
      fontSize: size,
      fontWeight: FontWeight.bold,
      color: color,
      letterSpacing: letterSpacing,
    );
  }

  static TextStyle mediumTextStyle({
    double size = 14,
    Color color = Colors.black,
    double letterSpacing = 0.2,
  }) {
    return TextStyle(
      fontSize: size,
      fontWeight: FontWeight.w500,
      color: color,
      letterSpacing: letterSpacing,
    );
  }

  static TextStyle secondaryTextStyle({
    double size = 14,
    Color? color,
    double letterSpacing = 0.2,
  }) {
    return TextStyle(
      fontSize: size,
      fontWeight: FontWeight.normal,
      color: color ?? AppColors.textSecondary,
      letterSpacing: letterSpacing,
    );
  }

  static TextStyle primaryTextStyle({
    double size = 14,
    Color? color,
    double letterSpacing = 0.2,
  }) {
    return TextStyle(
      fontSize: size,
      fontWeight: FontWeight.normal,
      color: color ?? AppColors.textPrimary,
      letterSpacing: letterSpacing,
    );
  }
}
""",

    "splashscreen": """import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:{package_name}/core/services/session_provider.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;
    
    final session = ref.read(sessionServiceProvider);
    final loggedIn = await session.isLoggedIn();
    
    if (loggedIn) {
      context.go('/home');
    } else {
      context.go('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 20),
            Text('Nexa Framework initializing...', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
""",

    "error_page": """import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ErrorPage extends StatelessWidget {
  final int? statusCode;
  final String? message;

  const ErrorPage({super.key, this.statusCode, this.message});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Error')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(
                'An error occurred ${statusCode != null ? "($statusCode)" : ""}',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                message ?? 'Something went wrong. Please try again.',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => context.go('/home'),
                child: const Text('Go Home'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
""",

    "location_disabled": """import 'package:flutter/material.dart';

class LocationServiceDisabledWidget extends StatelessWidget {
  const LocationServiceDisabledWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.location_off, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              const Text(
                'Location Service Disabled',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Please enable location services in your device settings to continue using the application.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
""",

    "app_router": """import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:{package_name}/core/presentation/splash/splashscreen.dart';
import 'package:{package_name}/core/presentation/widget/error_page.dart';
import 'package:{package_name}/core/presentation/widget/location_service_disabled_widget.dart';
import 'package:{package_name}/core/services/app_navigator.dart';

// Placeholder modular routes arrays to be injected by CLI later
// [NEXA_ROUTE_IMPORTS]

final GoRouter appRouter = GoRouter(
  navigatorKey: AppNavigator.navigatorKey,
  initialLocation: '/splash',
  routes: [
    GoRoute(path: '/', redirect: (context, state) => '/splash'),
    GoRoute(path: '/splash', builder: (context, state) => const SplashScreen()),
    GoRoute(
      path: "/error",
      builder: (context, state) {
        final extra = state.extra as Map<String, dynamic>?;
        final statusCode = extra?["statusCode"];
        final message = extra?["message"];
        return ErrorPage(statusCode: statusCode, message: message);
      },
    ),
    GoRoute(
      path: '/location-disabled',
      builder: (_, __) => const LocationServiceDisabledWidget(),
    ),
    // Placeholder for routes dynamically added by Nexa CLI:
    // [NEXA_ROUTES_ARRAY]
  ],
);
""",

    "main": """import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{package_name}/core/router/app_router.dart';
import 'package:{package_name}/core/theme/app_theme.dart';

void main() {{
  runApp(
    const ProviderScope(
      child: ProviderResetApp(),
    ),
  );
}}

class ProviderResetApp extends StatefulWidget {{
  const ProviderResetApp({{super.key}});

  @override
  State<ProviderResetApp> createState() => _ProviderResetAppState();
}}

class _ProviderResetAppState extends State<ProviderResetApp> {{
  Key _key = UniqueKey();

  void resetApp() {{
    setState(() {{
      _key = UniqueKey();
    }});
  }}

  @override
  Widget build(BuildContext context) {{
    return Container(
      key: _key,
      child: MaterialApp.router(
        title: '{project_name} Nexa App',
        theme: AppTheme.lightTheme,
        routerConfig: appRouter,
        debugShowCheckedModeBanner: false,
      ),
    );
  }}
}}
"""
}

class FlutterNewCommand(BaseCommand):
    """
    Initialize a new Nexa modular Clean Architecture Flutter project.
    """
    def run(self):
        if not self.args:
            self.logger.error("Project name required")
            return

        project_name = self.args[0].lower().replace("-", "_")
        self.logger.step(f"Initializing Nexa Flutter project: {project_name}...")

        # 1. Execute native flutter create
        try:
            self.logger.info("Executing native 'flutter create'...")
            subprocess.run([
                "flutter", "create", 
                "--org", "com.nexa",
                "--platforms", "android,ios",
                project_name
            ], check=True, shell=(os.name == 'nt'))
        except Exception as e:
            self.logger.error(f"Failed to execute flutter create: {e}")
            return

        project_dir = os.path.join(os.getcwd(), project_name)
        if not os.path.exists(project_dir):
            self.logger.error("Flutter project directory was not created.")
            return

        # 2. Patch dependencies in pubspec.yaml
        pubspec_path = os.path.join(project_dir, "pubspec.yaml")
        if os.path.exists(pubspec_path):
            self.logger.info("Patching pubspec.yaml dependencies...")
            self.patch_pubspec(pubspec_path)
        else:
            self.logger.error("pubspec.yaml not found!")
            return

        # 3. Create Core directory structures
        core_folders = [
            "lib/core/services",
            "lib/core/router",
            "lib/core/utils",
            "lib/core/theme",
            "lib/core/presentation/splash",
            "lib/core/presentation/widget",
            "lib/modules"
        ]
        
        for folder in core_folders:
            os.makedirs(os.path.join(project_dir, folder), exist_ok=True)

        # 4. Generate Core templates
        self.logger.info("Generating Nexa Core libraries and sizing engines...")
        
        files_to_write = {
            "lib/core/services/app_navigator.dart": TEMPLATES["app_navigator"],
            "lib/core/services/session_service.dart": TEMPLATES["session_service"],
            "lib/core/services/session_provider.dart": TEMPLATES["session_provider"],
            "lib/core/services/http_service.dart": TEMPLATES["http_service"],
            "lib/core/utils/size_utils.dart": TEMPLATES["size_utils"],
            "lib/core/utils/app_constants.dart": TEMPLATES["app_constants"],
            "lib/core/utils/app_dimensions.dart": TEMPLATES["app_dimensions"],
            "lib/core/utils/color_constants.dart": TEMPLATES["color_constants"],
            "lib/core/theme/app_theme.dart": TEMPLATES["app_theme"],
            "lib/core/presentation/splash/splashscreen.dart": TEMPLATES["splashscreen"],
            "lib/core/presentation/widget/error_page.dart": TEMPLATES["error_page"],
            "lib/core/presentation/widget/location_service_disabled_widget.dart": TEMPLATES["location_disabled"],
            "lib/core/router/app_router.dart": TEMPLATES["app_router"],
            "lib/main.dart": TEMPLATES["main"]
        }

        for rel_path, content in files_to_write.items():
            formatted_content = content.replace(
                "{package_name}", project_name
            ).replace(
                "{project_name}", project_name.capitalize()
            ).replace(
                "{{", "{"
            ).replace(
                "}}", "}"
            )
            full_path = os.path.join(project_dir, rel_path)
            with open(full_path, "w") as f:
                f.write(formatted_content)

        # 5. Create default placeholders for login & home modules
        self.logger.info("Creating initial placeholder modules...")
        self.create_placeholder_module(project_dir, project_name, "login")
        self.create_placeholder_module(project_dir, project_name, "home")

        self.logger.success(f"Nexa Flutter Project '{project_name}' has been successfully created!")
        self.logger.info(f"Navigate to your project using: cd {project_name}")
        self.logger.info("Run 'flutter pub get' to fetch all packages.")

    def patch_pubspec(self, path):
        with open(path, "r") as f:
            lines = f.readlines()

        new_lines = []
        in_dependencies = False
        patched = False

        for line in lines:
            new_lines.append(line)
            if line.strip() == "dependencies:":
                in_dependencies = True
                
            if in_dependencies and not patched:
                # Append Nexa required dependencies
                nexa_deps = [
                    "  flutter_riverpod: ^2.5.1\n",
                    "  go_router: ^14.0.0\n",
                    "  dio: ^5.4.0\n",
                    "  shared_preferences: ^2.2.0\n",
                    "  intl: ^0.19.0\n",
                    "  nb_utils: ^10.0.0\n",
                    "  lottie: ^3.1.0\n",
                    "  geolocator: ^12.0.0\n",
                    "  geocoding: ^3.0.0\n",
                    "  permission_handler: ^11.0.0\n"
                ]
                new_lines.extend(nexa_deps)
                patched = True
                in_dependencies = False

        with open(path, "w") as f:
            f.writelines(new_lines)

    def create_placeholder_module(self, project_dir, package_name, module_name):
        mod_dir = os.path.join(project_dir, f"lib/modules/{module_name}")
        os.makedirs(os.path.join(mod_dir, "presentation"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "application"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "data/models"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "data/repository"), exist_ok=True)

        class_name = module_name.capitalize()

        # Page Template
        page_code = f"""import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class {class_name}Page extends ConsumerWidget {{
  const {class_name}Page({{super.key}});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{class_name} Page'),
      ),
      body: const Center(
        child: Text('Welcome to {class_name} module boilerplate!'),
      ),
    );
  }}
}}
"""
        with open(os.path.join(mod_dir, f"presentation/{module_name}_page.dart"), "w") as f:
            f.write(page_code)

        # Route Template (with package: prefix)
        route_code = f"""import 'package:go_router/go_router.dart';
import 'package:{package_name}/modules/{module_name}/presentation/{module_name}_page.dart';

final {module_name}ModuleRoutes = <GoRoute>[
  GoRoute(
    path: '/{module_name}',
    name: '{module_name}_route',
    builder: (context, state) => const {class_name}Page(),
  ),
];
"""
        with open(os.path.join(mod_dir, "presentation/routes.dart"), "w") as f:
            f.write(route_code)

        # Auto register this placeholder module in app_router.dart
        router_path = os.path.join(project_dir, "lib/core/router/app_router.dart")
        if os.path.exists(router_path):
            with open(router_path, "r") as f:
                router_code = f.read()

            import_tag = "// [NEXA_ROUTE_IMPORTS]"
            array_tag = "// [NEXA_ROUTES_ARRAY]"

            new_import = f"import 'package:{package_name}/modules/{module_name}/presentation/routes.dart';\n{import_tag}"
            new_array = f"...{module_name}ModuleRoutes,\n    {array_tag}"

            router_code = router_code.replace(import_tag, new_import)
            router_code = router_code.replace(array_tag, new_array)

            with open(router_path, "w") as f:
                f.write(router_code)

def handle(args):
    cmd = FlutterNewCommand(args)
    cmd.run()
