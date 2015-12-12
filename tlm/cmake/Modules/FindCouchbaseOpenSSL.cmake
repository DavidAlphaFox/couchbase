# Locate openssl library
# This module defines
#  OPENSSL_FOUND, if false, do not try to link with openssl
#  OPENSSL_LIBRARIES, Library path and libs
#  OPENSSL_INCLUDE_DIR, where to find the ICU headers

FIND_PATH(OPENSSL_INCLUDE_DIR openssl/ssl.h
          HINTS
               ENV OPENSSL_DIR
          PATH_SUFFIXES include
          PATHS
               ~/Library/Frameworks
               /Library/Frameworks
               /usr/local
               /opt/local
               /opt/csw
               /opt/openssl
               /opt)



FIND_LIBRARY(OPENSSL_SSL_LIBRARY
             NAMES ssl libssl32 ssleay32
             HINTS
                 ENV OPENSSL_DIR
             PATHS
                 ~/Library/Frameworks
                 /Library/Frameworks
                 /usr/local
                 /opt/local
                 /opt/csw
                 /opt/openssl
                 /opt)

FIND_LIBRARY(OPENSSL_CRYPT_LIBRARY
             NAMES crypto libeay32
             HINTS
                 ENV OPENSSL_DIR
             PATHS
                 ${DEPS_LIB_DIR}
                 ~/Library/Frameworks
                 /Library/Frameworks
                 /usr/local
                 /opt/local
                 /opt/csw
                 /opt/openssl
                 /opt)


IF (OPENSSL_SSL_LIBRARY AND OPENSSL_CRYPT_LIBRARY)
   SET(OPENSSL_LIBRARIES ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPT_LIBRARY})
ENDIF(OPENSSL_SSL_LIBRARY AND OPENSSL_CRYPT_LIBRARY)

IF (OPENSSL_LIBRARIES AND OPENSSL_INCLUDE_DIR)
  MESSAGE(STATUS "Found openssl in ${OPENSSL_INCLUDE_DIR} : ${OPENSSL_LIBRARIES}")
ELSE (OPENSSL_LIBRARIES AND OPENSSL_INCLUDE_DIR)
  MESSAGE(FATAL_ERROR "Can't build Couchbase without openssl")
ENDIF (OPENSSL_LIBRARIES AND OPENSSL_INCLUDE_DIR)

MARK_AS_ADVANCED(OPENSSL_INCLUDE_DIR OPENSSL_LIBRARIES)
