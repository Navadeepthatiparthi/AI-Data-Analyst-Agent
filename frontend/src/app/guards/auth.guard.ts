import { inject } from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import {
  catchError,
  map,
  of
} from 'rxjs';

import {
  AuthService
} from '../services/auth.service';


export const authGuard: CanActivateFn = () => {

  const authService =
    inject(AuthService);

  const router =
    inject(Router);


  /*
   * No token at all.
   */
  if (!authService.getToken()) {

    return router.createUrlTree([
      '/login'
    ]);

  }


  /*
   * Ask FastAPI to validate the JWT
   * and identify the current user.
   */
  return authService
    .getCurrentUser()
    .pipe(

      map(user => {

        /*
         * Keep the latest authenticated
         * user information.
         */
        sessionStorage.setItem(
          'ai_analyst_user',
          JSON.stringify(user)
        );

        return true;

      }),

      catchError(() => {

        /*
         * Token is invalid or expired.
         */
        authService.logout();

        return of(
          router.createUrlTree([
            '/login'
          ])
        );

      })

    );

};