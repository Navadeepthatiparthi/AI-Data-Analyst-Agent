import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (
  request,
  next
) => {

  const token =
    sessionStorage.getItem(
      'ai_analyst_access_token'
    );

  /*
   * No token means this is probably a public
   * request such as login or registration.
   */
  if (!token) {
    return next(request);
  }

  /*
   * Attach the JWT to the outgoing request.
   */
  const authenticatedRequest =
    request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });

  return next(
    authenticatedRequest
  );
};