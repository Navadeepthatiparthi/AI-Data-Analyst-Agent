import { CommonModule } from '@angular/common';

import {
  Component
} from '@angular/core';

import {
  FormsModule
} from '@angular/forms';

import {
  Router,
  RouterLink
} from '@angular/router';

import {
  AuthService
} from '../../services/auth.service';


@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class RegisterComponent {

  fullName = '';

  email = '';

  password = '';

  loading = false;

  errorMessage = '';

  successMessage = '';


  constructor(
    private authService: AuthService,
    private router: Router
  ) {}


  register(): void {

    this.errorMessage = '';

    this.successMessage = '';


    if (
      !this.fullName.trim() ||
      !this.email.trim() ||
      !this.password
    ) {

      this.errorMessage =
        'Please complete all fields.';

      return;

    }


    if (this.password.length < 8) {

      this.errorMessage =
        'Password must contain at least 8 characters.';

      return;

    }


    this.loading = true;


    this.authService
      .register({
        full_name: this.fullName.trim(),
        email: this.email.trim(),
        password: this.password
      })
      .subscribe({

        next: () => {

          this.loading = false;

          this.successMessage =
            'Account created successfully. Redirecting to sign in...';

          setTimeout(() => {

            this.router.navigate([
              '/login'
            ]);

          }, 1000);

        },

        error: error => {

          console.error(
            'Registration error:',
            error
          );

          this.loading = false;

          this.errorMessage =
            error?.error?.detail ||
            'Unable to create your account.';

        }

      });

  }

}