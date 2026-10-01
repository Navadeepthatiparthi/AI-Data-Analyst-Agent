import { Routes } from '@angular/router';

import { DashboardComponent } from './pages/dashboard/dashboard';

import { authGuard } from './guards/auth.guard';


export const routes: Routes = [

  

  // Default route

  {

    path: '',

    redirectTo: 'dashboard',

    pathMatch: 'full'

  },


  // Authentication


  {

    path: 'login',

    loadComponent: () =>

      import('./pages/login/login')

        .then(

          module => module.LoginComponent

        )

  },

  {

    path: 'register',

    loadComponent: () =>

      import('./pages/register/register')

        .then(

          module => module.RegisterComponent

        )

  },


  // Dashboard

  // Dashboard can show the onboarding/upload state.

  {

    path: 'dashboard',

    component: DashboardComponent,

    canActivate: [authGuard]

  },


 
  // My Datasets


  {

    path: 'datasets',

    loadComponent: () =>

      import('./pages/datasets/datasets')

        .then(

          module => module.DatasetsComponent

        ),

    canActivate: [authGuard]

  },


 
  // Analytics

  {

    path: 'analytics/:datasetId',

    loadComponent: () =>

      import('./pages/analytics/analytics')

        .then(

          module => module.AnalyticsComponent

        ),

    canActivate: [authGuard]

  },


  {

    path: 'analytics',

    loadComponent: () =>

      import('./pages/analytics/analytics')

        .then(

          module => module.AnalyticsComponent

        ),

    canActivate: [authGuard]

  },


  // AI Analyst

  

  {

    path: 'ai-analyst/:datasetId',

    loadComponent: () =>

      import('./pages/ai-analyst/ai-analyst')

        .then(

          module => module.AiAnalystComponent

        ),

    canActivate: [authGuard]

  },


  {

    path: 'ai-analyst',

    loadComponent: () =>

      import('./pages/ai-analyst/ai-analyst')

        .then(

          module => module.AiAnalystComponent

        ),

    canActivate: [authGuard]

  },


  // Query History


  {

    path: 'history',

    loadComponent: () =>

      import('./pages/history/history')

        .then(

          module => module.HistoryComponent

        ),

    canActivate: [authGuard]

  },


  // Unknown route


  {

    path: '**',

    redirectTo: 'dashboard'

  }

];