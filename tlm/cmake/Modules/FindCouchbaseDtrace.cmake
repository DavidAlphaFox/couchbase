# stupid systemtap use a binary named dtrace as well..

IF (NOT ${CMAKE_SYSTEM_NAME} STREQUAL "Linux")

FIND_PROGRAM(DTRACE dtrace)
IF (DTRACE)
   SET(ENABLE_DTRACE True CACHE BOOL "Whether DTrace has been found")
   MESSAGE(STATUS "Found dtrace in ${DTRACE}")

   IF (CMAKE_SYSTEM_NAME MATCHES "SunOS")
      SET(DTRACE_NEED_INSTUMENT True CACHE BOOL
          "Whether DTrace should instrument object files")
   ENDIF (CMAKE_SYSTEM_NAME MATCHES "SunOS")
ENDIF (DTRACE)

MARK_AS_ADVANCED(DTRACE_NEED_INSTUMENT ENABLE_DTRACE DTRACE)

ENDIF (NOT ${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
