"""
This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Foobar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from SSR.ssr_app import create_app

application = create_app()

if __name__ == '__main__':
  application.run()
