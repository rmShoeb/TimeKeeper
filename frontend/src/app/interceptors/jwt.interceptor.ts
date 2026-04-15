import { HttpInterceptorFn } from '@angular/common/http';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const token = sessionStorage.getItem('jwt_token');

  console.log('[INTERCEPTOR] Request to:', req.url);
  console.log('[INTERCEPTOR] Token found:', !!token);

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    console.log('[INTERCEPTOR] Authorization header added');
  }

  return next(req);
};
