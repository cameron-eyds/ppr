import type { Route } from 'vue-router'
import { RouteNames } from '@/enums'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { useNavigation } from '@/composables'

const { goToRoute } = useNavigation()

/** Returns True if route requires authentication, else False. */
function requiresAuth (route: Route): boolean {
  return route.matched.some(r => r.meta?.requiresAuth)
}

/** Returns True if user is authenticated, else False. */
function isAuthenticated (): boolean {
  // FUTURE: also check that token isn't expired!
  return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
}

/** Returns True if route is Signin, else False. */
// eslint-disable-next-line
function isSigninRoute (route: Route): boolean {
  return Boolean(route.name === 'signin')
}

/** Returns True if route is Signout, else False. */
// eslint-disable-next-line
function isSignoutRoute (route: Route): boolean {
  return Boolean(route.name === 'signout')
}

/** Returns True if route is Login success, else False. */
function isLogin (route: Route): boolean {
  return Boolean(route.name === RouteNames.LOGIN)
}

/** Returns True if route is Login success, else False. */
function isLoginSuccess (route: Route): boolean {
  return Boolean(route.name === RouteNames.LOGIN && route.hash)
}

export default defineNuxtRouteMiddleware( (to) => {
  if (isLoginSuccess(to)) {
    // this route is to verify login
    navigateTo({
      name: RouteNames.SIGN_IN,
      query: { redirect: to.query.redirect }
    })
  } else {
    if (requiresAuth(to) && !isAuthenticated()) {
      // this route needs authentication, so re-route to login
      navigateTo({ name: RouteNames.LOGIN, query: { redirect: to.fullPath } })
      // return goToRoute(RouteNames.LOGIN, { redirect: to.fullPath })
    } else {
      if (isLogin(to) && isAuthenticated()) {
        // this route is to dashboard after login
        navigateTo({ name: RouteNames.DASHBOARD })
      } else {
        // otherwise just proceed normally
        navigateTo()
      }
    }
  }
})