@ECHO OFF
SET DIR=%~dp0
IF NOT EXIST "%DIR%gradle\wrapper\gradle-wrapper.jar" (
 ECHO gradle-wrapper.jar is not bundled. Open this project in Android Studio, or run gradle wrapper --gradle-version 8.13.
 EXIT /B 1
)
java -classpath "%DIR%gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
